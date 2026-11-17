"""
ReportForge Python SDK v2.0.0
Universal Document & Report Engine with In-Process Rust Core v2.0 and Cloud API Client.
"""

from .native import ReportForgeEngine
from .builder import (
    ReportDocument,
    PageConfigBuilder,
    ColumnBuilder,
    RowBuilder,
    TableBuilder,
    TableColumnBuilder,
    ContainerBuilder,
    TextBuilder,
)
from .client import ReportForgeClient
from .response import ReportResponse
from .exceptions import (
    ReportForgeSDKError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    ServerError,
    TimeoutError,
)

__version__ = "2.0.0"

def extract_text(pdf_bytes: bytes) -> str:
    """Extracts text from PDF bytes using native Rust Core v2.0."""
    return ReportForgeEngine.extract_text(pdf_bytes)

def extract_document(pdf_bytes: bytes, options=None) -> dict:
    """Extracts structured document data (pages, metadata) from PDF bytes using native Rust Core v2.0."""
    return ReportForgeEngine.extract_document(pdf_bytes, options)

__all__ = [
    # In-Process Native Engine
    "ReportForgeEngine",
    "extract_text",
    "extract_document",
    # Fluent Builders
    "ReportDocument",
    "PageConfigBuilder",
    "ColumnBuilder",
    "RowBuilder",
    "TableBuilder",
    "TableColumnBuilder",
    "ContainerBuilder",
    "TextBuilder",
    # Remote HTTP Client
    "ReportForgeClient",
    "ReportResponse",
    # Exceptions
    "ReportForgeSDKError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "ServerError",
    "TimeoutError",
]
