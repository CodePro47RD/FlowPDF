"""
Local filesystem storage backend for ReportForge.
"""

from __future__ import annotations
import os
import io
import time
from pathlib import Path
from typing import BinaryIO, Optional
from .base import BaseStorage
from ..core.exceptions import StorageError


class LocalStorage(BaseStorage):
    """
    Stores documents and assets on the local filesystem.
    """

    def __init__(self, base_dir: Union[str, Path] = "media/reports", base_url: str = "/media/reports/"):
        self.base_dir = Path(base_dir).resolve()
        self.base_url = base_url.rstrip("/") + "/"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _resolve(self, name: str) -> Path:
        p = (self.base_dir / name).resolve()
        try:
            p.relative_to(self.base_dir)
        except ValueError:
            raise StorageError(f"Path traversal detected in storage key: {name}")
        return p

    def save(self, name: str, content: bytes, content_type: str = "application/pdf") -> str:
        target = self._resolve(name)
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(target, "wb") as f:
                f.write(content)
            return name
        except OSError as e:
            raise StorageError(f"Failed to save file '{name}': {e}") from e

    def open(self, name: str) -> BinaryIO:
        target = self._resolve(name)
        if not target.exists():
            raise StorageError(f"File '{name}' does not exist.")
        try:
            return open(target, "rb")
        except OSError as e:
            raise StorageError(f"Failed to open file '{name}': {e}") from e

    def exists(self, name: str) -> bool:
        return self._resolve(name).exists()

    def delete(self, name: str) -> bool:
        target = self._resolve(name)
        if target.exists():
            try:
                target.unlink()
                return True
            except OSError as e:
                raise StorageError(f"Failed to delete file '{name}': {e}") from e
        return False

    def get_url(self, name: str, expiry_seconds: int = 3600) -> str:
        # For local storage, returns local API download URL or media URL
        return f"{self.base_url}{name.lstrip('/')}"

    def cleanup_older_than(self, max_age_seconds: int) -> int:
        """Remove temporary files older than max_age_seconds."""
        now = time.time()
        deleted_count = 0
        for item in self.base_dir.glob("**/*"):
            if item.is_file():
                if now - item.stat().st_mtime > max_age_seconds:
                    try:
                        item.unlink()
                        deleted_count += 1
                    except OSError:
                        pass
        return deleted_count
