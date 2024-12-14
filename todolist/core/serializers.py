from rest_framework import serializers
from .models import Todo, Tag
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class TodoSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    status = serializers.CharField(required=False)  # or other appropriate field type
    description = serializers.CharField(required=False)  # Make this optional

    def validate(self, data):
        errors = {}

        # Check required fields
        if self.context["request"].method in ["POST"]:
            required_fields = ["title"]
            errors = {}
            for field in required_fields:
                if field not in data or not data[field]:
                    errors[field] = "This field is required"
            if errors:
                raise serializers.ValidationError(errors)

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def validate_tags(self, value):
        MAX_TAGS = 5
        if value and len(value) > MAX_TAGS:
            raise serializers.ValidationError(f"Cannot add more than {MAX_TAGS} tags.")

        # Check for duplicate tags (case-insensitive)
        tag_names = [tag["name"].strip().lower() for tag in value]
        if len(tag_names) != len(set(tag_names)):
            raise serializers.ValidationError("Tags must be unique.")

        return value

    def validate_due_date(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value

    class Meta:
        model = Todo
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "due_date",
            "status",
            "tags",
        ]
        read_only_fields = ["created_at"]

    def create(self, validated_data):
        user = validated_data.pop("user", None)

        if not user and "request" in self.context:
            user = self.context["request"].user

        tags_data = validated_data.pop("tags", [])

        # Create the todo item
        todo = Todo.objects.create(user=user, **validated_data)

        # Add tags if they exist
        if tags_data:
            for tag_data in tags_data:
                tag, _ = Tag.objects.get_or_create(
                    name__iexact=tag_data["name"],
                    user=user,  # Use the todo's user for the tag
                    defaults={"name": tag_data["name"].strip().lower(), "user": user},
                )
                todo.tags.add(tag)

        return todo

    def update(self, instance, validated_data):
        # Pop out 'user' from validated_data if it's present to avoid duplication
        user = validated_data.pop("user", None)

        # If 'user' is not found in validated_data, get it from the context
        if not user and "request" in self.context:
            user = self.context["request"].user

        tags_data = validated_data.pop("tags", None)

        # Update todo item fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # Update tags if provided
        if tags_data is not None:
            instance.tags.clear()

            for tag_data in tags_data:
                tag, _ = Tag.objects.get_or_create(
                    name__iexact=tag_data["name"],
                    user=user,  # Ensure tag is associated with todo's user
                    defaults={"name": tag_data["name"].strip().lower(), "user": user},
                )
                instance.tags.add(tag)

        return instance
