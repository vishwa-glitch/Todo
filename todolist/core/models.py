from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower


class Todo(models.Model):
    # Choices for task status
    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("WORKING", "Working"),
        ("PENDING_REVIEW", "Pending Review"),
        ("COMPLETED", "Completed"),
        ("OVERDUE", "Overdue"),
        ("CANCELLED", "Cancelled"),
    ]

    # Timestamp when task is created
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Timestamp of task creation (automatically set)"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="todos",
        help_text="User who created the todo",
    )
    # Title of the task, mandatory field with max length
    title = models.CharField(
        max_length=100,  # Enforces max length
        null=False,  # Prevents null values
        blank=False,  # Prevents empty strings
        help_text="Title of the task (max 100 characters)",
    )

    # Optional description of the task
    description = models.TextField(
        max_length=1000,  # Enforces max length
        null=True,  # Allows null values
        blank=True,  # Allows empty strings
        help_text="Detailed description of the task (max 1000 characters)",
    )

    # Optional due date for task completion
    due_date = models.DateTimeField(
        null=True,  # Allows null
        blank=True,  # Allows empty value
        help_text="Optional expected completion date",
    )

    # Status of the task with predefined choices
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="OPEN",  # Default value is "OPEN"
        help_text="Current status of the task",
    )

    # Many-to-Many relationship for tags
    tags = models.ManyToManyField(
        "Tag",
        blank=True,  # Optional relationship
        help_text="Optional tags associated with the task",
        related_name="todos",
    )

    # Clean method to validate business rules
    def clean(self):
        if self.due_date:
            if timezone.is_naive(self.due_date):
                self.due_date = timezone.make_aware(
                    self.due_date, timezone.get_current_timezone()
                )
        # Prevent due dates in the past
        if self.due_date and self.due_date < timezone.now():
            raise ValidationError("Due date cannot be in the past.")
        # Ensure title is not empty
        if not self.title:
            raise ValidationError("Title cannot be empty.")

    # Save method to ensure validation is run
    def save(self, *args, **kwargs):
        self.full_clean()  # Trigger all validations
        return super().save(*args, **kwargs)

    # Method to set tags for the task
    def set_tags(self, tag_names):
        self.tags.clear()  # Remove existing tags
        for tag_name in set(tag_names):
            normalized_tag = tag_name.strip().lower()  # Normalize tag
            tag, created = Tag.objects.get_or_create(name=normalized_tag)
            self.tags.add(tag)  # Associate tag with the task

    def __str__(self):
        return f"{self.title} - {self.status}"

    class Meta:
        ordering = ["-created_at"]  # Sort tasks by newest first
        verbose_name = "Todo Item"  # Singular form for admin
        verbose_name_plural = "Todo Items"  # Plural form for admin


class Tag(models.Model):
    """
    Model for task tags with case-insensitive unique names.
    """

    name = models.CharField(max_length=50, help_text="Unique tag name")
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tags",
        help_text="User who created the tag",
    )

    # Clean method to normalize tag name
    def clean(self):
        self.name = self.name.strip().lower()  # Normalize to lowercase

    def save(self, *args, **kwargs):
        self.clean()  # Normalize before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def todo_count(self):
        return str(self.todos.count())  # Count associated todos

    class Meta:
        # Unique constraint for lowercase tag name per user
        constraints = [
            UniqueConstraint(
                Lower("name"), "user", name="unique_lowercase_tag_name_per_user"
            )
        ]
