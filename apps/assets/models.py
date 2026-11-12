import uuid
from django.db import models
from apps.authentication.models import Application


class Asset(models.Model):
    """
    Uploaded tenant asset such as logos, signature graphics, or custom TTF fonts.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="assets",
    )
    name = models.CharField(max_length=120, db_index=True)
    asset_type = models.CharField(
        max_length=20,
        choices=[("image", "Image"), ("font", "Font")],
        default="image",
    )
    file = models.FileField(upload_to="assets/%Y/%m/")
    mime_type = models.CharField(max_length=100, blank=True)
    file_size = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reportforge_assets"
        verbose_name = "Asset"
        verbose_name_plural = "Assets"
        unique_together = ("application", "name")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.asset_type})"
