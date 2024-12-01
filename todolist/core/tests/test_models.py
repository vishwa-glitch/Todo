from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from core.models import Todo, Tag
from django.contrib import admin
class TodoModelTest(TestCase):
    def setUp(self):
        # Create a tag for testing
        self.test_tag = Tag.objects.create(name="Test Tag")
        
        # Create a base todo item for testing
        self.todo = Todo.objects.create(
            title="Test Todo",
            description="Test Description",
            due_date=timezone.now() + timedelta(days=1),
            status='OPEN'
        )

    def test_todo_creation(self):
        """
        Test that a Todo item can be created with valid data
        """
        self.assertEqual(self.todo.title, "Test Todo")
        self.assertEqual(self.todo.description, "Test Description")
        self.assertEqual(self.todo.status, 'OPEN')
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
            title="Another Todo",
            description="Another Description"
        )
        self.assertEqual(new_todo.status, 'OPEN')

    def test_todo_past_due_date_validation(self):
        """
        Test validation prevents due dates in the past
        """
        past_date = timezone.now() - timedelta(days=1)
        
        with self.assertRaises(ValidationError):
            invalid_todo = Todo(
                title="Past Due Todo",
                description="Past Due Description",
                due_date=past_date
            )
            invalid_todo.full_clean()

    def test_todo_empty_title_validation(self):
        """
        Test validation prevents empty title
        """
        with self.assertRaises(ValidationError):
            invalid_todo = Todo(
                title="",
                description="Some Description"
            )
            invalid_todo.full_clean()

    def test_todo_tag_assignment(self):
        """
        Test tag assignment method
        """
        # Create some test tags
        tag_names = ['Work', 'Urgent', 'work']  # Note the duplicate with different case
        
        self.todo.set_tags(tag_names)
        
        # Check that tags are added correctly (case-insensitive, no duplicates)
        self.assertEqual(self.todo.tags.count(), 2)
        tag_names = [tag.name for tag in self.todo.tags.all()]
        self.assertIn('work', tag_names)
        self.assertIn('urgent', tag_names)

    def test_tag_creation_and_normalization(self):
        """
        Test tag creation and name normalization
        """
        # Create a tag with mixed case and extra spaces
        tag = Tag(name="  TestTag  ")
        tag.full_clean()
        
        # Check that the tag name is normalized
        self.assertEqual(tag.name, 'testtag')

class TagModelTest(TestCase):
    def test_tag_creation(self):
        """
        Test basic tag creation
        """
        tag = Tag.objects.create(name="Python")
        self.assertEqual(tag.name, "python")
        self.assertEqual(str(tag), "python")

    def test_tag_uniqueness(self):
        """
        Test that tags are case-insensitive
        """
        tag = Tag.objects.create(name="python")
        tag.clean()  # Manually call the clean method to normalize the name
        # Attempting to create a tag with same name (different case) should work without duplicating
        with self.assertRaises(Exception):
            Tag.objects.create(name="Python")

    def test_tag_name_normalization(self):
        """
        Test tag name normalization
        """
        tag = Tag(name="  Machine Learning  ")
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
          status='OPEN'
      )
      
      # Check that no tags are associated
      self.assertEqual(todo_without_tags.tags.count(), 0)
    def test_due_date_naive(self):
        naive_due_date = timezone.now() + timedelta(days=1)
        todo_naive = Todo.objects.create(
            title="Naive Todo",
            description="Test Naive Todo",
            due_date=naive_due_date,
            status='OPEN'
        )

        todo_naive.clean()
        # Compare the timezone info properly
        self.assertEqual(todo_naive.due_date.tzinfo.tzname(None), timezone.get_current_timezone().tzname(None))


    def test_due_date_aware(self):
        # Create a naive datetime
        naive_due_date = timezone.now().replace(tzinfo=None) + timedelta(days=1)
        
        # Make it aware
        aware_due_date = timezone.make_aware(naive_due_date)

        todo_aware = Todo.objects.create(
            title="Aware Todo",
            description="Test Aware Todo",
            due_date=aware_due_date,
            status='OPEN'
        )

        todo_aware.clean()
        self.assertTrue(timezone.is_aware(todo_aware.due_date))

    def test_due_date_invalid(self):
        # Pass a datetime object (not a string)
        invalid_due_date = timezone.now() - timedelta(days=1)
        todo_invalid = Todo(
            title="Invalid Todo",
            description="Test Invalid Todo",
            due_date=invalid_due_date,  # Use a valid datetime here
            status='OPEN'
        )
        # Check if clean method raises a ValidationError for invalid due_date
        with self.assertRaises(ValidationError):
            todo_invalid.clean()


