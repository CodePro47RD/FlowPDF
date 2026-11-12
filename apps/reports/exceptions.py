from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from engine.core.exceptions import ReportForgeError, TemplateSyntaxError, SecurityError


def custom_exception_handler(exc, context):
    """
    Standardizes error responses across ReportForge.
    Translates engine-specific exceptions into standard DRF JSON structures.
    """
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            "success": False,
            "status_code": response.status_code,
            "error": response.data.get("detail", str(response.data)),
            "details": response.data,
        }
        return response

    if isinstance(exc, TemplateSyntaxError):
        return Response(
            {
                "success": False,
                "status_code": status.HTTP_400_BAD_REQUEST,
                "error": "Template Syntax Error",
                "details": str(exc),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, SecurityError):
        return Response(
            {
                "success": False,
                "status_code": status.HTTP_403_FORBIDDEN,
                "error": "Security Violation",
                "details": str(exc),
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    if isinstance(exc, ReportForgeError):
        return Response(
            {
                "success": False,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error": "Document Engine Error",
                "details": str(exc),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return None
