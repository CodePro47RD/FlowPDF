import uuid
from django.db import models
from apps.authentication.models import Application
from apps.templates.models import Template


class ReportJob(models.Model):
    """
    Tracks state, metrics, and storage location for generated reports.
    """
    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="reports",
    )
    template = models.ForeignKey(
        Template,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_reports",
    )
    format = models.CharField(max_length=10, default="pdf")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    storage_key = models.CharField(max_length=512, blank=True)
    file_size = models.PositiveIntegerField(default=0)
    page_count = models.PositiveIntegerField(default=1)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "reportforge_reports"
        verbose_name = "Report Job"
        verbose_name_plural = "Report Jobs"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Report {self.id} [{self.status}]"
