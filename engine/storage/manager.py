"""
Storage manager factory for ReportForge.
"""

from __future__ import annotations
import os
from typing import Optional
from .base import BaseStorage
from .local import LocalStorage
from .s3 import S3Storage


_storage_instance: Optional[BaseStorage] = None


def get_storage() -> BaseStorage:
    """Return the configured global storage instance."""
    global _storage_instance
    if _storage_instance is not None:
        return _storage_instance

    backend_type = os.getenv("REPORTFORGE_STORAGE_BACKEND", "local").lower()

    if backend_type == "s3":
        _storage_instance = S3Storage(
            bucket_name=os.getenv("AWS_STORAGE_BUCKET_NAME", "reportforge-documents"),
            endpoint_url=os.getenv("AWS_S3_ENDPOINT_URL", None),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", None),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", None),
            region_name=os.getenv("AWS_S3_REGION_NAME", "us-east-1"),
        )
    else:
        base_dir = os.getenv("REPORTFORGE_STORAGE_DIR", "media/reports")
        _storage_instance = LocalStorage(base_dir=base_dir)

    return _storage_instance


def set_storage(storage: BaseStorage) -> None:
    """Override storage instance (useful for testing)."""
    global _storage_instance
    _storage_instance = storage
