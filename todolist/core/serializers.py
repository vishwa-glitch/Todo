from rest_framework import serializers
from .models import Todo, Tag
from django.utils import timezone
from django.core.exceptions import ValidationError

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class TodoSerializer(serializers.ModelSerializer):
    # Comprehensive serializer for Todo model,
    # Handles complex serialization and validation requirements
    tags = TagSerializer(many=True, read_only=False, required=False)
    status = serializers.CharField(required=True)  # or other appropriate field type
    description = serializers.CharField(required=False)  # Make this optional
    def validate(self, data):
        # Add status validation at the serializer level
        if 'status' not in data:
            raise serializers.ValidationError({"status": "Status is required."})
        return data
    
    def validate_tags(self, value):
        if value:
            tag_names = [tag['name'].strip().lower() for tag in value]
            if len(tag_names) != len(set(tag_names)):  # Check for duplicates
                raise serializers.ValidationError("Tags must be unique.")
            # Additional validation for tags if needed
        return value
    
    def validate_due_date(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value
    class Meta:
        model = Todo
        fields = [
            'id', 
            'title', 
            'description', 
            'created_at', 
            'due_date', 
            'status', 
            'tags'
        ]
        read_only_fields = ['created_at']

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        
        todo = Todo.objects.create(**validated_data)

        if tags_data:
            for tag_data in tags_data:
                # Use case-insensitive lookup and creation
                tag, _ = Tag.objects.get_or_create(
                    name__iexact=tag_data['name'], 
                    defaults={'name': tag_data['name'].strip().lower()}
                )
                todo.tags.add(tag)
        
        return todo

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        
        # Update todo item fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        # Update tags if provided
        if tags_data is not None:
            instance.tags.clear()
            
            for tag_data in tags_data:
                tag, _ = Tag.objects.get_or_create(
                    name__iexact=tag_data['name'], 
                    defaults={'name': tag_data['name'].strip().lower()}
                )
                instance.tags.add(tag)
        
        return instance