"""
ReportForge core exceptions hierarchy.
"""


class ReportForgeError(Exception):
    """Base exception for all ReportForge errors."""
    pass


class LayoutError(ReportForgeError):
    """Raised when an error occurs during measurement or layout."""
    pass


class LayoutOverflowError(LayoutError):
    """Raised when an unbreakable component cannot fit inside available space."""
    pass


class RenderError(ReportForgeError):
    """Raised when an error occurs while rendering to a canvas or file."""
    pass


class TemplateError(ReportForgeError):
    """Base error for template parsing and validation."""
    pass


class TemplateSyntaxError(TemplateError):
    """Raised when a JSON template does not conform to the schema."""
    pass


class TemplateDataError(TemplateError):
    """Raised when data binding fails due to missing or invalid fields."""
    pass


class AssetError(ReportForgeError):
    """Raised when an external asset (image, font) cannot be loaded."""
    pass


class SecurityError(ReportForgeError):
    """Raised when an insecure operation (unauthorized file access) is attempted."""
    pass


class StorageError(ReportForgeError):
    """Raised when storage operations fail."""
    pass
