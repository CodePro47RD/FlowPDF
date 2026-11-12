"""
S3 and MinIO compatible storage backend for ReportForge.
"""

from __future__ import annotations
import io
from typing import BinaryIO, Optional
from .base import BaseStorage
from ..core.exceptions import StorageError


class S3Storage(BaseStorage):
    """
    Object storage backend supporting AWS S3, Cloudflare R2, and self-hosted MinIO.
    """

    def __init__(
        self,
        bucket_name: str,
        endpoint_url: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: str = "us-east-1",
    ):
        self.bucket_name = bucket_name
        self.endpoint_url = endpoint_url
        self.region_name = region_name

        try:
            import boto3
            self._client = boto3.client(
                "s3",
                endpoint_url=endpoint_url,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region_name,
            )
        except ImportError:
            self._client = None

    def _ensure_client(self):
        if self._client is None:
            raise StorageError("boto3 is required for S3Storage. Install it with `pip install boto3`.")

    def save(self, name: str, content: bytes, content_type: str = "application/pdf") -> str:
        self._ensure_client()
        try:
            self._client.put_object(
                Bucket=self.bucket_name,
                Key=name,
                Body=content,
                ContentType=content_type,
            )
            return name
        except Exception as e:
            raise StorageError(f"Failed to upload '{name}' to S3: {e}") from e

    def open(self, name: str) -> BinaryIO:
        self._ensure_client()
        try:
            response = self._client.get_object(Bucket=self.bucket_name, Key=name)
            return response["Body"]
        except Exception as e:
            raise StorageError(f"Failed to fetch '{name}' from S3: {e}") from e

    def exists(self, name: str) -> bool:
        self._ensure_client()
        try:
            self._client.head_object(Bucket=self.bucket_name, Key=name)
            return True
        except Exception:
            return False

    def delete(self, name: str) -> bool:
        self._ensure_client()
        try:
            self._client.delete_object(Bucket=self.bucket_name, Key=name)
            return True
        except Exception as e:
            raise StorageError(f"Failed to delete '{name}' from S3: {e}") from e

    def get_url(self, name: str, expiry_seconds: int = 3600) -> str:
        self._ensure_client()
        try:
            url = self._client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": name},
                ExpiresIn=expiry_seconds,
            )
            return str(url)
        except Exception as e:
            raise StorageError(f"Failed to generate presigned URL for '{name}': {e}") from e
