from django.test import TestCase
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.contrib.admin import site
from core.models import Todo, Tag
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from core.admin import TodoAdmin, TagAdmin
from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model


User = get_user_model()

class AdminTests(TestCase):
    def setUp(self):
        # Create a superuser
        self.user = User.objects.create_superuser(
            username="admin", password="password", email="admin@example.com"
        )
        self.client.login(username="admin", password="password")

        # Initialize RequestFactory and AdminSite for admin tests
        self.factory = RequestFactory()
        self.site = AdminSite()

        # Create a Tag instance
        self.tag = Tag.objects.create(name="Python", user=self.user)

        # Create Todo instances
        self.todo1 = Todo.objects.create(
            title="Todo 1",
            description="Description 1",
            status="OPEN",
            created_at=timezone.now(),
            user=self.user,
        )
        self.todo2 = Todo.objects.create(
            title="Todo 2",
            description="Description 2",
            status="OPEN",
            created_at=timezone.now(),
            user=self.user,
        )

        # Associate tags with todos
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
            description="A test description",
            status="OPEN",
            user = self.user
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
            user = self.user
        )

        self.assertEqual(todo.due_date, future_due_date)
        self.assertIsNotNone(todo.created_at)  # Ensure created_at is set

    def test_todo_count_with_todos(self):
        # Test todo_count when there are related Todos
        count = self.tag.todo_count()  # Call the method on the Tag instance
        self.assertEqual(count, "2")  # Ensure it returns "2" as a string

    def test_todo_count_with_no_todos(self):
        # Test todo_count when there are no related Todos
        empty_tag = Tag.objects.create(name="Empty List", user = self.user)
        count = empty_tag.todo_count()
        self.assertEqual(count, "0")  # Ensure it returns "0" as a string

    def test_save_model_validation_error(self):
        # Attempt to save an invalid Todo instance via the admin
        invalid_todo = Todo(
            title="",  # Invalid: Title is required
            description="Invalid Todo",
            status="OPEN",
            user=self.user,
        )
        with self.assertRaises(ValidationError):  # Now it checks for ValidationError
            invalid_todo.full_clean()  # Perform validation
            invalid_todo.save()

    def test_todo_count_method_in_tag_admin(self):
        # Test that the todo_count method works in TagAdmin

        # Fetch the admin change list for the Tag model
        response = self.client.get(reverse("admin:core_tag_changelist"))  # Replace 'app' with your app's name

        # Check if the count of todos for the tag is correct
        # 'Python' tag should have 2 associated todos
        self.assertContains(response, "2") 

    def test_save_model_validates_and_saves_object(self):
        # Step 1: Initialize the admin instance
        admin_instance = TodoAdmin(Todo, self.site)

        # Step 2: Create a mock POST request (simulating admin action)
        request = self.factory.post("/admin/todo/todo/")
        request.user = self.user  # Set the request user to the admin user

        # Step 3: Create a Todo instance and modify it
        todo = Todo.objects.create(
            title="Original Todo",
            description="Description before saving",
            status="OPEN",
            user=self.user,
        )
        todo.title = "Updated Todo"
        todo.description = "Updated description"

        # Step 4: Call save_model and validate behavior
        admin_instance.save_model(request, todo, None, change=True)

        # Step 5: Fetch the updated instance and assert changes
        updated_todo = Todo.objects.get(pk=todo.pk)

        # Assert that the object was validated and saved
        self.assertEqual(updated_todo.title, "Updated Todo")
        self.assertEqual(updated_todo.description, "Updated description")
        self.assertEqual(updated_todo.status, "OPEN")

    def test_admin_login(self):
        # Test if admin login works correctly
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)

    def test_save_model_prevents_created_at_change(self):
        # Initialize the admin instance
        admin_instance = TodoAdmin(Todo, self.site)

        # Simulate a POST request
        request = self.factory.post("/admin/todo/todo/")

        # Attempt to change the `created_at` field of a Todo instance
        original_created_at = self.todo1.created_at
        self.todo1.title = "Updated Todo"
        self.todo1.created_at = timezone.now()  # Attempt to modify created_at
        admin_instance.save_model(request, self.todo1, None, change=True)

        # Fetch the updated object
        updated_todo = Todo.objects.get(pk=self.todo1.pk)

        # Assert that the `created_at` field has not changed
        self.assertEqual(updated_todo.created_at, original_created_at)

        # Assert that the title was updated successfully
        self.assertEqual(updated_todo.title, "Updated Todo")
