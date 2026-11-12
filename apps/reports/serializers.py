from rest_framework import serializers
from .models import ReportJob
from engine.storage.manager import get_storage


class GenerateReportRequestSerializer(serializers.Serializer):
    template = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Name or UUID of a saved template",
    )
    document = serializers.DictField(
        required=False,
        allow_null=True,
        help_text="Inline document definition schema (if not using a saved template)",
    )
    data = serializers.DictField(
        required=False,
        default=dict,
        help_text="Data variables and collections to bind into template expressions",
    )
    format = serializers.ChoiceField(
        choices=["pdf", "html"],
        default="pdf",
        help_text="Output format (default: pdf)",
    )
    async_mode = serializers.BooleanField(
        default=False,
        help_text="Whether to process via background Celery worker",
    )
    response_type = serializers.ChoiceField(
        choices=["binary", "json"],
        default="binary",
        help_text="For synchronous generation: 'binary' streams PDF directly, 'json' returns download link",
    )

    def validate(self, attrs):
        if not attrs.get("template") and not attrs.get("document"):
            raise serializers.ValidationError(
                "Either 'template' (stored template name/id) or 'document' (inline layout definition) must be provided."
            )
        return attrs


class ReportJobResponseSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = ReportJob
        fields = [
            "id",
            "status",
            "format",
            "file_size",
            "page_count",
            "download_url",
            "error_message",
            "created_at",
            "completed_at",
        ]

    def get_download_url(self, obj) -> str:
        if obj.status == ReportJob.STATUS_COMPLETED and obj.storage_key:
            request = self.context.get("request")
            if request is not None:
                return request.build_absolute_uri(f"/api/v1/reports/{obj.id}/download/")
            return f"/api/v1/reports/{obj.id}/download/"
        return ""
