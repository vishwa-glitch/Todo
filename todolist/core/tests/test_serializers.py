from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from datetime import timedelta
from core.models import Todo, Tag
from core.serializers import TodoSerializer, TagSerializer

class TodoSerializerTests(TestCase):
    def setUp(self):
        # Create some initial test data
        self.tag1 = Tag.objects.create(name='Work')
        self.tag2 = Tag.objects.create(name='Personal')
        
        # Sample valid todo data
        self.valid_todo_data = {
            'title': 'Test Todo',
            'description': 'A test todo item',
            'status': 'OPEN',
            'due_date': timezone.now() + timedelta(days=7),
            'tags': [
                {'name': 'Work'},
                {'name': 'Personal'}
            ]
        }

    def test_todo_serializer_update_with_tags(self):

      """
      Test updating a todo item with new tags
      """
    # Create initial todo with existing tags
      initial_serializer = TodoSerializer(data=self.valid_todo_data)
      initial_serializer.is_valid()
      original_todo = initial_serializer.save()

      # Prepare update data with new tags
      update_data = {
          'status': 'OPEN',
          'tags': [
              {'name': 'NewTag1'},
              {'name': 'NewTag2'}
          ]
      }
      
      # Update the todo
      update_serializer = TodoSerializer(original_todo, data=update_data, partial=True)
      self.assertTrue(update_serializer.is_valid(), update_serializer.errors)
      updated_todo = update_serializer.save()

      # Verify tags were replaced
      self.assertEqual(updated_todo.tags.count(), 2)
      updated_tag_names = set(updated_todo.tags.values_list('name', flat=True))
      self.assertEqual(updated_tag_names, {'newtag1', 'newtag2'})

    def test_todo_serializer_update_remove_tags(self):
        """
        Test updating a todo item to remove all tags
        """
        # Create initial todo with tags
        initial_serializer = TodoSerializer(data=self.valid_todo_data)
        initial_serializer.is_valid()
        original_todo = initial_serializer.save()

        # Prepare update data with empty tags list
        update_data = {
            'status': 'OPEN',
            'tags': []
        }
        
        # Update the todo
        update_serializer = TodoSerializer(original_todo, data=update_data, partial=True)
        self.assertTrue(update_serializer.is_valid(), update_serializer.errors)
        updated_todo = update_serializer.save()

        # Verify all tags were removed
        self.assertEqual(updated_todo.tags.count(), 0)

    def test_todo_serializer_update_partial_fields(self):
        """
        Test updating a todo item with partial field updates
        """
        # Create initial todo
        initial_serializer = TodoSerializer(data=self.valid_todo_data)
        initial_serializer.is_valid()
        original_todo = initial_serializer.save()

        # Prepare partial update
        update_data = {
            'status': 'OPEN',
            'title': 'Updated Title',
            'tags': [{'name': 'Important'}]
        }
        
        # Update the todo
        update_serializer = TodoSerializer(original_todo, data=update_data, partial=True)
        self.assertTrue(update_serializer.is_valid(), update_serializer.errors)
        updated_todo = update_serializer.save()

        # Verify specific updates
        self.assertEqual(updated_todo.title, 'Updated Title')
        self.assertEqual(updated_todo.tags.count(), 1)
        self.assertEqual(list(updated_todo.tags.values_list('name', flat=True))[0], 'important')

    def test_validate_status_is_present(self):
            """
            Test that if 'status' field is present, validation passes.
            """
            # Create valid data with 'status' field
            data = {
                'title': 'Sample Todo',
                'status': 'OPEN',
                'tags': [{'name': 'tag1'}]
            }

            # Initialize the serializer with the valid data
            serializer = TodoSerializer(data=data)
            if not serializer.is_valid():
                print("Validation errors:", serializer.errors)
            # Check if validation passes without error
            self.assertTrue(serializer.is_valid())