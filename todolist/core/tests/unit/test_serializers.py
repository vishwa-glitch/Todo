from rest_framework.test import APIRequestFactory
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from datetime import timedelta
from core.models import Todo, Tag
from core.serializers import TodoSerializer, TagSerializer
from rest_framework import status
from rest_framework.test import APIClient

class TodoSerializerTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser', 
            password='12345'
        )

        # Create tags for the specific user
        self.tag1 = Tag.objects.create(name="Work", user=self.user)
        self.tag2 = Tag.objects.create(name="Personal", user=self.user)

        # Sample valid todo data
        self.valid_todo_data = {
            "title": "Test Todo",
            "description": "A test todo item",
            "status": "OPEN",
            "due_date": timezone.now() + timedelta(days=7),
            "user": self.user,  # Add user to the data
            "tags": [{"name": "Work"}, {"name": "Personal"}],
        }

        # Create a request factory instance
        self.factory = APIRequestFactory()
        self.client = APIClient()  # Use APIClient here
        self.client.force_authenticate(user=self.user)  # Authenticate the client

    def test_todo_serializer_update_with_tags(self):
        """
        Test updating a todo item with new tags
        """
        # Create initial todo with existing tags
        request = self.factory.post('/todos/', self.valid_todo_data)
        request.user = self.user  # Assign user to the request

        context = {'request': request}  # Pass the request to the context
        initial_serializer = TodoSerializer(data=self.valid_todo_data, context=context)
        initial_serializer.is_valid(raise_exception=True)
        original_todo = initial_serializer.save()

        # Prepare update data with new tags
        update_data = {
            "status": "OPEN",
            "tags": [{"name": "NewTag1"}, {"name": "NewTag2"}],
        }

        # Update the todo
        update_request = self.factory.patch(f'/todos/{original_todo.id}/', update_data)
        update_request.user = self.user  # Assign user to the request

        update_context = {'request': update_request}  # Pass the request to the context
        update_serializer = TodoSerializer(
            original_todo, data=update_data, partial=True, context=update_context
        )
        self.assertTrue(update_serializer.is_valid(), update_serializer.errors)
        updated_todo = update_serializer.save()

        # Verify tags were replaced
        self.assertEqual(updated_todo.tags.count(), 2)
        updated_tag_names = set(updated_todo.tags.values_list("name", flat=True))
        self.assertEqual(updated_tag_names, {"newtag1", "newtag2"})

    def test_todo_serializer_update_remove_tags(self):
        """
        Test updating a todo item to remove all tags
        """
        # Create initial todo with tags
        request = self.factory.post('/todos/', self.valid_todo_data)
        request.user = self.user  # Assign user to the request

        context = {'request': request}  # Pass the request to the context
        initial_serializer = TodoSerializer(data=self.valid_todo_data, context=context)
        initial_serializer.is_valid(raise_exception=True)
        original_todo = initial_serializer.save()

        # Prepare update data with empty tags list
        update_data = {"status": "OPEN", "tags": []}

        # Update the todo
        update_request = self.factory.patch(f'/todos/{original_todo.id}/', update_data)
        update_request.user = self.user  # Assign user to the request

        update_context = {'request': update_request}  # Pass the request to the context
        update_serializer = TodoSerializer(
            original_todo, data=update_data, partial=True, context=update_context
        )
        self.assertTrue(update_serializer.is_valid(), update_serializer.errors)
        updated_todo = update_serializer.save()

        # Verify all tags were removed
        self.assertEqual(updated_todo.tags.count(), 0)

    def test_todo_serializer_update_partial_fields(self):
        """
        Test updating a todo item with partial field updates
        """
        # Create initial todo
        request = self.factory.post('/todos/', self.valid_todo_data)
        request.user = self.user  # Assign user to the request

        context = {'request': request}  # Pass the request to the context
        initial_serializer = TodoSerializer(data=self.valid_todo_data, context=context)
        initial_serializer.is_valid(raise_exception=True)
        original_todo = initial_serializer.save()

        # Prepare partial update
        update_data = {
            "status": "OPEN",
            "title": "Updated Title",
            "tags": [{"name": "Important"}],
        }

        # Update the todo
        update_request = self.factory.patch(f'/todos/{original_todo.id}/', update_data)
        update_request.user = self.user  # Assign user to the request

        update_context = {'request': update_request}  # Pass the request to the context
        update_serializer = TodoSerializer(
            original_todo, data=update_data, partial=True, context=update_context
        )
        self.assertTrue(update_serializer.is_valid(), update_serializer.errors)
        updated_todo = update_serializer.save()

        # Verify specific updates
        self.assertEqual(updated_todo.title, "Updated Title")
        self.assertEqual(updated_todo.tags.count(), 1)
        self.assertEqual(
            list(updated_todo.tags.values_list("name", flat=True))[0], "important"
        )

    def test_validate_status_is_present(self):
        """
        Test that if 'status' field is present, validation passes.
        """
        # Create valid data with 'status' field
        data = {
            "title": "Sample Todo", 
            "status": "OPEN", 
            "tags": [{"name": "tag1"}],
            "user": self.user  # Add user to the data
        }

        # Initialize the serializer with the valid data
        context = {'request': type('TestRequest', (), {'method': 'POST'})}
        serializer = TodoSerializer(data=data, context=context)
        # Check if validation passes without error
        self.assertTrue(serializer.is_valid())

    def test_create_todo_missing_required_fields(self):
        data = {}  # Empty data to trigger missing required fields
        
        self.client.force_authenticate(user=self.user)

        response = self.client.post("/core/api/todos/", data, format="json")
        
        # Check for validation errors
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
        self.assertEqual(response.data['title'][0], 'This field is required.')  # Updated message


    def test_create_todo_due_date_in_past(self):
            due_date = timezone.now() - timedelta(days=1)  # Set due date to the past
            data = {
                'title': 'Test Todo',
                'due_date': due_date.isoformat(),
            }
            
            response = self.client.post("/core/api/todos/", data, format="json")
            
            # Check for validation error
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('due_date', response.data)
            self.assertEqual(response.data['due_date'][0], 'Due date cannot be in the past.')
    
    def test_create_todo_with_too_many_tags(self):
            tags = [{'name': 'tag' + str(i)} for i in range(6)]  # 6 tags, one more than the max
            data = {
                'title': 'Test Todo',
                'tags': tags,
            }
            self.client.force_authenticate(user=self.user)

            response = self.client.post("/core/api/todos/", data, format="json")
            
            # Check for validation error
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('tags', response.data)
            self.assertEqual(response.data['tags'][0], 'Cannot add more than 5 tags.')
    
    def test_create_todo_with_duplicate_tags(self):
        tags = [{'name': 'Tag1'}, {'name': 'Tag1'}]  # Duplicate tags
        data = {
            'title': 'Test Todo',
            'tags': tags,
        }
        self.client.force_authenticate(user=self.user)

        response = self.client.post("/core/api/todos/", data, format="json")
        
        # Check for validation error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('tags', response.data)
        self.assertEqual(response.data['tags'][0], 'Tags must be unique.')

    def test_create_todo_with_invalid_data(self):
            data = {
                'title': '',  # Empty title should trigger required field error
                'due_date': timezone.now() - timedelta(days=1),  # Due date in the past
                'tags': [{'name': 'Tag1'}, {'name': 'Tag1'}],  # Duplicate tags
            }
            self.client.force_authenticate(user=self.user)

            response = self.client.post("/core/api/todos/", data, format="json")
            
            # Check for validation errors
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('title', response.data)
            self.assertIn('due_date', response.data)
            self.assertIn('tags', response.data)