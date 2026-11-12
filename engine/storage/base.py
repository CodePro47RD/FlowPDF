"""
Abstract storage backend interface for ReportForge.
Enables transparent switching between Local disk, MinIO, and AWS S3.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import BinaryIO, Optional


class BaseStorage(ABC):
    """Abstract file storage backend."""

    @abstractmethod
    def save(self, name: str, content: bytes, content_type: str = "application/pdf") -> str:
        """Save file content and return relative storage key / identifier."""
        pass

    @abstractmethod
    def open(self, name: str) -> BinaryIO:
        """Open a file stream for reading."""
        pass

    @abstractmethod
    def exists(self, name: str) -> bool:
        """Check whether a file exists."""
        pass

    @abstractmethod
    def delete(self, name: str) -> bool:
        """Delete a file from storage."""
        pass

    @abstractmethod
    def get_url(self, name: str, expiry_seconds: int = 3600) -> str:
        """Get a public or presigned temporary download URL."""
        pass
