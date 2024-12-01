from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from core.models import Todo, Tag
from django.utils import timezone
from datetime import timedelta

class TodoAPITestCase(APITestCase):
    """
    Integration Tests for Todo API Endpoints
    Covers CRUD operations and authentication
    """
    def setUp(self):
        """
        Prepare test environment
        """
        # Create test user
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpassword'
        )
        self.client.login(username='testuser', password='testpassword')

        # Create sample todo items
        self.todo1 = Todo.objects.create(
            title='First Todo',
            description='First Description',
            status='OPEN'
        )
        self.todo2 = Todo.objects.create(
            title='Second Todo',
            description='Second Description',
            status='WORKING'
        )

    def test_create_todo_item(self):
        """
        Test creating a new todo item via API
        """
        data = {
            'title': 'New Todo',
            'description': 'New Description',
            'status': 'OPEN',
            'tags': [{'name': 'Personal'}]
        }
        response = self.client.post('/core/api/todos/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Todo.objects.count(), 3)
        self.assertEqual(response.data['title'], 'New Todo')

    def test_list_todo_items(self):
        """
        Test retrieving all todo items
        """
        response = self.client.get('/core/api/todos/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_update_todo_item(self):
        """
        Test updating an existing todo item
        """
        updated_data = {
            'title': 'Updated Todo',
            'description': self.todo1.description,
            'status': 'COMPLETED'
        }
        response = self.client.put(
            f'/core/api/todos/{self.todo1.id}/', 
            updated_data, 
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.todo1.refresh_from_db()
        self.assertEqual(self.todo1.title, 'Updated Todo')
        self.assertEqual(self.todo1.status, 'COMPLETED')

    def test_delete_todo_item(self):
        """
        Test deleting a todo item
        """
        response = self.client.delete(f'/core/api/todos/{self.todo1.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Todo.objects.filter(id=self.todo1.id).exists())

    def test_create_todo_invalid_tags(self):
        data = {
            'title': 'New Todo',
            'description': 'Description',
            'tags': [{'name': 'Personal'}, {'name': 'personal'}]  # Duplicate tags
        }
        response = self.client.post('/core/api/todos/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_todo_missing_fields(self):
        data = {'description': 'Description'}
        response = self.client.post('/core/api/todos/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_todo_invalid_due_date(self):
        data = {
            'title': 'Past Todo',
            'description': 'Description',
            'due_date': timezone.now() - timedelta(days=1),
            'status': 'OPEN'
        }
        response = self.client.post('/core/api/todos/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
