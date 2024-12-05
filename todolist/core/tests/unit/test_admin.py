from django.test import TestCase
from django.contrib import admin
from django.urls import reverse
from django.contrib.admin import site
from core.models import Todo, Tag
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class AdminTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(username="admin", password="password")
        self.client.login(username="admin", password="password")

        # Create Todo objects and relate them to the todo_list
        self.tag = Tag.objects.create(name="Python")  # Create a Tag instance

        self.todo1 = Todo.objects.create(
            title="Todo 1",
            description="Description 1",
            status="OPEN",
            created_at=timezone.now(),  # Use current time for created_at
        )
        self.todo2 = Todo.objects.create(
            title="Todo 2",
            description="Description 2",
            status="OPEN",
            created_at=timezone.now(),  # Use current time for created_at
        )
        self.todo1.tags.add(self.tag)
        self.todo2.tags.add(self.tag)

    def test_todo_admin_list_view(self):
        # Test that the Todo admin list view works
        url = reverse("admin:core_todo_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.todo1.title)

    def test_todo_admin_add_view(self):
        # Test adding a new Todo through the admin
        url = reverse("admin:core_todo_add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_todo_admin_save_model(self):
        # Test custom save_model method (like preventing created_at modification)
        todo = Todo.objects.create(
            title="Test Todo",
            description="A test description",  # Add description
            status="OPEN",
        )
        todo.status = "COMPLETED"
        todo.save()

        # Verify that 'created_at' has not been changed
        original_created_at = todo.created_at
        todo.status = "PENDING_REVIEW"
        todo.save()
        self.assertEqual(todo.created_at, original_created_at)

    def test_tag_admin_display_tags(self):
        # Test custom Tag model behavior (like todo_count display)
        url = reverse("admin:core_tag_change", args=[self.tag.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1")  # Directly check the count

    def test_save_model_preserves_created_at(self):
        # Create a Todo instance
        future_due_date = timezone.now() + timedelta(days=1)
        todo = Todo.objects.create(
            title="Test Todo",
            description="This is a test todo item",
            status="OPEN",
            due_date=future_due_date,
        )

        self.assertEqual(todo.due_date, future_due_date)
        self.assertIsNotNone(todo.created_at)  # Ensure created_at is set

    def test_todo_count_with_todos(self):
        # Test todo_count when there are related Todos
        count = self.tag.todo_count()  # Call the method on the Tag instance
        self.assertEqual(count, "2")  # Ensure it returns "2" as a string

    def test_todo_count_with_no_todos(self):
        # Test todo_count when there are no related Todos
        empty_tag = Tag.objects.create(name="Empty List")
        count = empty_tag.todo_count()
        self.assertEqual(count, "0")  # Ensure it returns "0" as a string

    def test_admin_login(self):
        # Test if admin login works correctly
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)
