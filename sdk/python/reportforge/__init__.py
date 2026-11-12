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

__all__ = [
    # In-Process Native Engine
    "ReportForgeEngine",
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
