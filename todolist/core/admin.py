from django.contrib import admin
from django.utils.html import format_html
from .models import Todo, Tag

@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):

    list_display = (
        'title', 
        'status', 
        'created_at', 
        'due_date', 
        'display_tags',
        'status_color'
    )

    list_filter = (
        'status', 
        ('created_at', admin.DateFieldListFilter),
        ('due_date', admin.DateFieldListFilter)
    )

    search_fields = ['title', 'description']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description'),
            'description': 'Core details of the todo item'
        }),
        ('Status and Timing', {
            'fields': ('status', 'due_date'),
            'description': 'Task status and expected completion date'
        }),
        ('Tags', {
            'fields': ('tags',),
            'description': 'Optional tags for categorization'
        })
    )

    readonly_fields = ('created_at',)

    def display_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()]) or "No tags"
    display_tags.short_description = 'Tags'

    def status_color(self, obj):
        color_map = {
            'OPEN': 'green',
            'WORKING': 'blue',
            'PENDING_REVIEW': 'orange',
            'COMPLETED': 'green',
            'OVERDUE': 'red',
            'CANCELLED': 'gray'
        }
        color = color_map.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.status
        )
    status_color.short_description = 'Status'

    # Custom validation in admin
    def save_model(self, request, obj, form, change):

        # To Prevent changing created_at
        if change:
            original_obj = Todo.objects.get(pk=obj.pk)
            obj.created_at = original_obj.created_at
        
        # Perform custom validations
        obj.full_clean()
        super().save_model(request, obj, form, change)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'todo_count')
    search_fields = ['name']

    def todo_count(self, obj):
        count = obj.todo_set.count()
        return str(count)  # Explicitly convert to string
    todo_count.short_description = 'Number of Todos'


admin.site.site_header = 'AlgoBulls Todo Management'
admin.site.site_title = 'Todo Admin Portal'
admin.site.index_title = 'Welcome to Todo Administration'
