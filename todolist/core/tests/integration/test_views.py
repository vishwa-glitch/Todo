from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from core.models import Todo, Tag
import json


class TodoAPITestCase(APITestCase):
    """
    Comprehensive Integration Tests for Todo API Endpoints
    Covers CRUD operations, authentication, validation, and edge cases
    """

    def setUp(self):
        """
        Prepare test environment with multiple scenarios
        """
        # Create test users
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.another_user = User.objects.create_user(
            username="anotheruser", password="anotherpassword"
        )

        # Authenticate with the primary test user
        self.client.login(username="testuser", password="testpassword")

        # Create sample todo items
        self.todo1 = Todo.objects.create(
            title="First Todo",
            description="First Description",
            status="OPEN",
            user=self.user,
        )
        self.todo2 = Todo.objects.create(
            title="Second Todo",
            description="Second Description",
            status="WORKING",
            user=self.user,
        )

        # Create a tag for testing
        self.tag = Tag.objects.create(name="Personal", user=self.user)

    def test_create_todo_item_with_tags(self):
        """
        Test creating a new todo item with tags
        """
        data = {
            "title": "New Todo",
            "description": "New Description",
            "status": "OPEN",
            "tags": [{"name": "Work"}],
            "due_date": (timezone.now() + timedelta(days=7)).isoformat(),
        }
        response = self.client.post("/core/api/todos/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Todo.objects.count(), 3)
        self.assertEqual(response.data["title"], "New Todo")
        self.assertEqual(len(response.data["tags"]), 1)
        self.assertEqual(response.data["tags"][0]["name"], "work")

    def test_list_todo_items(self):
        """
        Test retrieving all todo items for the authenticated user
        """
        response = self.client.get("/core/api/todos/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only return todos for the authenticated user
        self.assertEqual(len(response.data), 2)

    def test_update_todo_item(self):
        """
        Test updating an existing todo item
        """
        updated_data = {
            "title": "Updated Todo",
            "description": self.todo1.description,
            "status": "WORKING",
            "tags": [{"name": "Personal"}],
            "due_date": (timezone.now() + timedelta(days=10)).isoformat(),
        }
        response = self.client.put(
            f"/core/api/todos/{self.todo1.id}/", updated_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.todo1.refresh_from_db()
        self.assertEqual(self.todo1.title, "Updated Todo")
        self.assertEqual(self.todo1.status, "WORKING")

    def test_partial_update_todo_item(self):
        """
        Test partial update of a todo item
        """
        updated_data = {"status": "COMPLETED"}
        response = self.client.patch(
            f"/core/api/todos/{self.todo1.id}/", updated_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.todo1.refresh_from_db()
        self.assertEqual(self.todo1.status, "COMPLETED")

    def test_delete_todo_item(self):
        """
        Test deleting a todo item
        """
        response = self.client.delete(f"/core/api/todos/{self.todo1.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Todo.objects.filter(id=self.todo1.id).exists())

    def test_create_todo_invalid_tags(self):
        """
        Test creating a todo with duplicate tags
        """
        data = {
            "title": "New Todo",
            "description": "Description",
            "tags": [
                {"name": "Personal"},
                {"name": "personal"},
            ],  # Case-insensitive duplicate
        }
        response = self.client.post("/core/api/todos/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_todo_missing_fields(self):
        """
        Test creating a todo with missing required fields
        """
        data = {"description": "Description"}
        response = self.client.post("/core/api/todos/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_todo_invalid_due_date(self):
        """
        Test creating a todo with a past due date
        """
        data = {
            "title": "Past Todo",
            "description": "Description",
            "due_date": (timezone.now() - timedelta(days=1)).isoformat(),
            "status": "OPEN",
        }
        response = self.client.post("/core/api/todos/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_access(self):
        """
        Test that unauthenticated users cannot access todo endpoints
        """
        # Logout the current user
        self.client.logout()

        # Try to create a todo
        data = {
            "title": "Unauthorized Todo",
            "description": "Unauthorized Description",
        }
        response = self.client.post("/core/api/todos/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Try to list todos
        response = self.client.get("/core/api/todos/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_todo_of_another_user(self):
        """
        Test that users cannot update todos belonging to other users
        """
        # Login with another user
        self.client.logout()
        self.client.login(username="anotheruser", password="anotherpassword")

        # Try to update the first user's todo
        updated_data = {
            "title": "Attempted Unauthorized Update",
        }
        response = self.client.patch(
            f"/core/api/todos/{self.todo1.id}/", updated_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_todo_with_max_tags(self):
        """
        Test creating a todo with maximum allowed tags
        """
        # Assuming a max of 5 tags per todo
        data = {
            "title": "Multi-Tag Todo",
            "description": "Description with multiple tags",
            "tags": [
                {"name": "Personal"},
                {"name": "Work"},
                {"name": "Urgent"},
                {"name": "Project"},
                {"name": "Important"},
            ],
        }
        response = self.client.post("/core/api/todos/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["tags"]), 5)

    def test_create_todo_exceed_max_tags(self):
        """
        Test creating a todo with more than maximum allowed tags
        """
        data = {
            "title": "Too Many Tags Todo",
            "description": "Description with too many tags",
            "tags": [
                {"name": "Personal"},
                {"name": "Work"},
                {"name": "Urgent"},
                {"name": "Project"},
                {"name": "Important"},
                {"name": "Extra"},
            ],
        }
        response = self.client.post("/core/api/todos/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
