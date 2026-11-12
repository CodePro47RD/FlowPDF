from rest_framework import serializers
from .models import Asset


class AssetSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = [
            "id",
            "name",
            "asset_type",
            "file",
            "mime_type",
            "file_size",
            "url",
            "created_at",
        ]
        read_only_fields = ["id", "file_size", "mime_type", "url", "created_at"]

    def get_url(self, obj) -> str:
        request = self.context.get("request")
        if obj.file and hasattr(obj.file, "url"):
            if request is not None:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return ""

    def create(self, validated_data):
        app = getattr(self.context["request"], "application", None)
        validated_data["application"] = app
        file_obj = validated_data.get("file")
        if file_obj:
            validated_data["file_size"] = file_obj.size
            validated_data["mime_type"] = getattr(file_obj, "content_type", "")
        return super().create(validated_data)
