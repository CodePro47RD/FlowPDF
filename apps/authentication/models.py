import secrets
import uuid
from django.db import models


class Application(models.Model):
    """
    Represents a client application / tenant consuming ReportForge.
    Enforces multi-tenancy isolation and API key authentication.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text="Human-readable application name")
    api_key = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text="Secret key for API authorization (starts with rf_live_)",
    )
    is_active = models.BooleanField(default=True)
    rate_limit_per_minute = models.PositiveIntegerField(default=120)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reportforge_applications"
        verbose_name = "Application"
        verbose_name_plural = "Applications"

    def __str__(self) -> str:
        return f"{self.name} ({self.api_key[:10]}...)"

    @classmethod
    def generate_api_key(cls) -> str:
        return f"rf_live_{secrets.token_urlsafe(32)}"

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = self.generate_api_key()
        super().save(*args, **kwargs)
