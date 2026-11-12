"""
Exception classes for the ReportForge Python SDK.
"""


class ReportForgeSDKError(Exception):
    """Base exception for all ReportForge SDK client errors."""
    pass


class AuthenticationError(ReportForgeSDKError):
    """Raised when API Key authentication fails (401/403)."""
    pass


class NotFoundError(ReportForgeSDKError):
    """Raised when a requested template or report is not found (404)."""
    pass


class ValidationError(ReportForgeSDKError):
    """Raised when request payload or template schema is invalid (400)."""
    pass


class ServerError(ReportForgeSDKError):
    """Raised when the ReportForge server encounters an internal error (500)."""
    pass


class TimeoutError(ReportForgeSDKError):
    """Raised when an asynchronous report job exceeds the timeout threshold."""
    pass
