from rest_framework import serializers
from pydantic import ValidationError as PydanticValidationError
from engine.templates.schema import DocumentTemplateSchema
from .models import Template


class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = [
            "id",
            "name",
            "version",
            "description",
            "definition",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_definition(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Template definition must be a valid JSON object.")
        try:
            # Validate through Pydantic document template schema
            DocumentTemplateSchema.model_validate(value)
        except PydanticValidationError as e:
            raise serializers.ValidationError(f"Invalid template layout schema: {e}")
        return value

    def create(self, validated_data):
        # Automatically attach the requesting tenant application
        app = getattr(self.context["request"], "application", None)
        validated_data["application"] = app
        return super().create(validated_data)
