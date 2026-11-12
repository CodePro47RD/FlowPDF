import uuid
from django.db import models
from apps.authentication.models import Application


class Template(models.Model):
    """
    Stored reusable document template for a specific tenant application.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="templates",
        help_text="Tenant that owns this template",
    )
    name = models.CharField(max_length=120, db_index=True)
    version = models.CharField(max_length=20, default="1.0")
    description = models.TextField(blank=True, default="")
    definition = models.JSONField(help_text="Document layout JSON definition")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reportforge_templates"
        verbose_name = "Template"
        verbose_name_plural = "Templates"
        unique_together = ("application", "name", "version")
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return f"{self.name} v{self.version} ({self.application.name})"
