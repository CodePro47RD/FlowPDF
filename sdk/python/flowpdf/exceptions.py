"""
Exception classes for the FlowPDF Python SDK.
"""


class FlowPdfSDKError(Exception):
    """Base exception for all FlowPDF SDK client errors."""
    pass


class AuthenticationError(FlowPdfSDKError):
    """Raised when API Key authentication fails (401/403)."""
    pass


class NotFoundError(FlowPdfSDKError):
    """Raised when a requested template or report is not found (404)."""
    pass


class ValidationError(FlowPdfSDKError):
    """Raised when request payload or template schema is invalid (400)."""
    pass


class ServerError(FlowPdfSDKError):
    """Raised when the FlowPDF server encounters an internal error (500)."""
    pass


class TimeoutError(FlowPdfSDKError):
    """Raised when an asynchronous report job exceeds the timeout threshold."""
    pass
