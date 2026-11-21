"""
FlowPDF Python SDK
Universal Document & Report Engine with In-Process Rust Core and Cloud API Client.
"""

from .native import FlowPdfEngine
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
from .client import FlowPdfClient
from .response import ReportResponse
from .exceptions import (
    FlowPdfSDKError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    ServerError,
    TimeoutError,
)

__version__ = "1.0.0"

def extract_text(pdf_bytes: bytes) -> str:
    """Extracts text from PDF bytes using native Rust Core."""
    return FlowPdfEngine.extract_text(pdf_bytes)

def extract_document(pdf_bytes: bytes, options=None) -> dict:
    """Extracts structured document data (pages, metadata) from PDF bytes using native Rust Core."""
    return FlowPdfEngine.extract_document(pdf_bytes, options)

__all__ = [
    # In-Process Native Engine
    "FlowPdfEngine",
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
    "FlowPdfClient",
    "ReportResponse",
    # Exceptions
    "FlowPdfSDKError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "ServerError",
    "TimeoutError",
]
