from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower

class Todo(models.Model):
    # Predefined status choices to match assignment requirements
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('WORKING', 'Working'),
        ('PENDING_REVIEW', 'Pending Review'),
        ('COMPLETED', 'Completed'),
        ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled')
    ]
    
    # Timestamp that cannot be modified after creation
    # auto_now_add ensures timestamp is set only once during object creation
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp of task creation (automatically set)"
    )
    
    # Complex Logic: Title field with strict validation constraints
    title = models.CharField(
        max_length=100,  # Enforces maximum length requirement
        null=False,      # Prevents null values
        blank=False,     # Prevents empty strings in forms
        help_text="Title of the task (max 100 characters)"
    )
    
    # Complex Logic: Description field with similar strict validation
    description = models.TextField(
        max_length=1000,  # Enforces maximum length requirement
        null=True,       # Prevents null values
        blank=True,      # Prevents empty strings in forms
        help_text="Detailed description of the task (max 1000 characters)"
    )
    
    # Complex Logic: Optional due date with past date prevention
    due_date = models.DateTimeField(
        null=True,   # Allows the field to be optional
        blank=True,  # Allows empty input in forms
        help_text="Optional expected completion date"
    )
    
    # Complex Logic: Status field with predefined choices
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='OPEN',  # Sets default status as OPEN
        help_text="Current status of the task"
    )
    
    # Complex Logic: Many-to-Many relationship for tags 
    # Allows multiple tags per todo item with unique constraint
    tags = models.ManyToManyField(
        'Tag', 
        blank=True,  # Optional tags
        help_text="Optional tags associated with the task",
        related_name='todos'
    )
    
    def clean(self):
        if self.due_date:
            if timezone.is_naive(self.due_date):
                self.due_date = timezone.make_aware(self.due_date, timezone.get_current_timezone())

        # Prevent due dates from being in the past
        if self.due_date and self.due_date < timezone.now():
            raise ValidationError("Due date cannot be in the past.")
        
        # Ensure title and description are not empty
        if not self.title:
            raise ValidationError("Title cannot be empty.")
    
    def save(self, *args, **kwargs):
    
        # Override save method
        '''
        Ensures full model validation is performed before saving:
        1. Runs full_clean() to trigger all validation methods
        2. Prevents saving invalid model instances
        3. Maintains data integrity at the model level
        '''

        self.full_clean()
        return super().save(*args, **kwargs)
    
    def set_tags(self, tag_names):
        # Clear existing tags to prevent duplicates
        self.tags.clear()
        
        # Create or get tags, avoiding duplicates
        for tag_name in set(tag_names):
            # Normalize tag: strip whitespace and convert to lowercase
            normalized_tag = tag_name.strip().lower()
            
            # Get or create tag, ensuring unique lowercase tags
            tag, created = Tag.objects.get_or_create(
                name=normalized_tag
            )
            
            # Add the tag to this todo item
            self.tags.add(tag)
    
    def __str__(self):
        return f"{self.title} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']  # Sort by newest first
        verbose_name = 'Todo Item'
        verbose_name_plural = 'Todo Items'

class Tag(models.Model):
    """
    1. Case-insensitive unique tag names
    2. Normalized tag storage
    """
    name = models.CharField(
        max_length=50,
        help_text="Unique tag name"
    )
    
    def clean(self):
        """
        Ensures:
        1. No leading/trailing whitespaces
        2. Converted to lowercase to prevent duplicates
        """
        self.name = self.name.strip().lower()


    def save(self, *args, **kwargs):
        self.clean()  # Call clean before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name  
    
    def todo_count(self):
        return str(self.todos.count())
    
    class Meta:
        # Complex Logic: Unique constraint on lowercase tag names
        constraints = [
            UniqueConstraint(Lower('name'), name='unique_lowercase_tag_name')
        ]