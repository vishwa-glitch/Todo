from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from core.models import Todo, Tag
from django.contrib import admin
from django.contrib.auth import get_user_model


class TodoModelTest(TestCase):
    def setUp(self):
        # Create a user for the tests
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpassword"
        )

        # Create a tag for testing, with the user assigned
        self.test_tag = Tag.objects.create(name="Test Tag", user=self.user)

        # Create a base todo item for testing
        self.todo = Todo.objects.create(
            title="Test Todo",
            description="Test Description",
            due_date=timezone.now() + timedelta(days=1),
            status="OPEN",
            user=self.user,  # Associate user with Todo
        )

    def test_todo_creation(self):
        """
        Test that a Todo item can be created with valid data
        """
        self.assertEqual(self.todo.title, "Test Todo")
        self.assertEqual(self.todo.description, "Test Description")
        self.assertEqual(self.todo.status, "OPEN")
        self.assertIsNotNone(self.todo.created_at)

    def test_todo_str_method(self):
        """
        Test the string representation of Todo
        """
        expected_str = f"{self.todo.title} - {self.todo.status}"
        self.assertEqual(str(self.todo), expected_str)

    def test_todo_default_status(self):
        """
        Test that the default status is 'OPEN'
        """
        new_todo = Todo.objects.create(
            title="Another Todo", description="Another Description", user=self.user
        )
        self.assertEqual(new_todo.status, "OPEN")

    def test_todo_past_due_date_validation(self):
        """
        Test validation prevents due dates in the past
        """
        past_date = timezone.now() - timedelta(days=1)

        with self.assertRaises(ValidationError):
            invalid_todo = Todo(
                title="Past Due Todo",
                description="Past Due Description",
                due_date=past_date,
                user=self.user,
            )
            invalid_todo.full_clean()

    def test_todo_empty_title_validation(self):
        """
        Test validation prevents empty title
        """
        with self.assertRaises(ValidationError):
            invalid_todo = Todo(
                title="", description="Some Description", user=self.user
            )
            invalid_todo.full_clean()

    def test_todo_tag_assignment(self):
        """
        Test tag assignment method
        """
        # Create some test tags, making sure to avoid duplicates by normalizing to lowercase
        tag_names = ["Work", "Urgent", "work"]  # Note the duplicate with different case

        # Create tags and associate them with the user, making sure no duplicates (case-insensitive)
        tags = []
        for name in tag_names:
            normalized_name = (
                name.strip().lower()
            )  # Normalize to lowercase to prevent duplicates
            tag, created = Tag.objects.get_or_create(
                name=normalized_name, user=self.user
            )
            tags.append(tag)

        # Assign the tags to the Todo item
        self.todo.set_tags([tag.name for tag in tags])

        # Check that tags are added correctly (case-insensitive, no duplicates)
        self.assertEqual(self.todo.tags.count(), 2)
        tag_names = [tag.name for tag in self.todo.tags.all()]
        self.assertIn("work", tag_names)
        self.assertIn("urgent", tag_names)

    def test_tag_creation_and_normalization(self):
        """
        Test tag creation and name normalization
        """
        # Create a tag with mixed case and extra spaces
        tag = Tag(name="  TestTag  ", user=self.user)
        tag.full_clean()

        # Check that the tag name is normalized
        self.assertEqual(tag.name, "testtag")


class TagModelTest(TestCase):
    def setUp(self):
        # Create a user for the tests
        self.user = get_user_model().objects.create_user(
            username="taguser", password="tagpassword"
        )

    def test_tag_creation(self):
        """
        Test basic tag creation
        """
        tag = Tag.objects.create(name="Python", user=self.user)
        self.assertEqual(tag.name, "python")
        self.assertEqual(str(tag), "python")

    def test_tag_uniqueness(self):
        """
        Test that tags are case-insensitive
        """
        tag = Tag.objects.create(name="python", user=self.user)
        tag.clean()  # Manually call the clean method to normalize the name

        # Attempting to create a tag with same name (different case) for the same user should fail
        with self.assertRaises(Exception):
            Tag.objects.create(name="Python", user=self.user)

    def test_tag_name_normalization(self):
        """
        Test tag name normalization
        """
        tag = Tag(name="  Machine Learning  ", user=self.user)
        tag.full_clean()

        self.assertEqual(tag.name, "machine learning")

    def test_todo_empty_tags(self):
        """
        Test that a Todo can be created with no tags
        """
        todo_without_tags = Todo.objects.create(
            title="Todo without Tags",
            description="Description",
            due_date=timezone.now() + timedelta(days=1),
            status="OPEN",
            user=self.user,
        )

        # Check that no tags are associated
        self.assertEqual(todo_without_tags.tags.count(), 0)

    def test_due_date_naive(self):
        naive_due_date = timezone.now() + timedelta(days=1)
        todo_naive = Todo.objects.create(
            title="Naive Todo",
            description="Test Naive Todo",
            due_date=naive_due_date,
            status="OPEN",
            user=self.user,
        )

        todo_naive.clean()
        # Compare the timezone info properly
        self.assertEqual(
            todo_naive.due_date.tzinfo.tzname(None),
            timezone.get_current_timezone().tzname(None),
        )

    def test_due_date_aware(self):
        # Create a naive datetime
        naive_due_date = timezone.now().replace(tzinfo=None) + timedelta(days=1)

        # Make it aware
        aware_due_date = timezone.make_aware(naive_due_date)

        todo_aware = Todo.objects.create(
            title="Aware Todo",
            description="Test Aware Todo",
            due_date=aware_due_date,
            status="OPEN",
            user=self.user,
        )

        todo_aware.clean()
        self.assertTrue(timezone.is_aware(todo_aware.due_date))

    def test_due_date_naive_becomes_aware(self):
        """
        Test that a naive due_date is automatically converted to an aware datetime
        """
        # Create a naive datetime
        naive_due_date = timezone.now().replace(tzinfo=None) + timedelta(days=1)

        # Create Todo with naive datetime
        todo = Todo.objects.create(
            title="Naive to Aware Todo",
            description="Test Naive to Aware Conversion",
            due_date=naive_due_date,
            status="OPEN",
            user=self.user,
        )

        # Verify that the due_date is now aware
        self.assertTrue(timezone.is_aware(todo.due_date))

        # Verify that the timezone matches the current timezone
        self.assertEqual(
            todo.due_date.tzinfo.tzname(None),
            timezone.get_current_timezone().tzname(None),
        )

    def test_due_date_invalid(self):
        # Pass a datetime object (not a string)
        invalid_due_date = timezone.now() - timedelta(days=1)
        todo_invalid = Todo(
            title="Invalid Todo",
            description="Test Invalid Todo",
            due_date=invalid_due_date,  # Use a valid datetime here
            status="OPEN",
            user=self.user,
        )
        # Check if clean method raises a ValidationError for invalid due_date
        with self.assertRaises(ValidationError):
            todo_invalid.clean()
