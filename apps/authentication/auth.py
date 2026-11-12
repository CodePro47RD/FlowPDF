from typing import Optional, Tuple
from django.contrib.auth.models import AnonymousUser
from rest_framework import authentication, exceptions
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from .models import Application


class APIKeyAuthentication(authentication.BaseAuthentication):
    """
    Authenticates requests using the 'X-API-Key' header or 'Authorization: Api-Key <token>'
    """

    def authenticate(self, request) -> Optional[Tuple[AnonymousUser, Application]]:
        api_key = request.headers.get("X-API-Key")

        if not api_key:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Api-Key ") or auth_header.startswith("Bearer rf_"):
                api_key = auth_header.split(" ", 1)[1].strip()

        if not api_key:
            # Let other authentications handle it
            return None

        try:
            app = Application.objects.get(api_key=api_key, is_active=True)
        except Application.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid or inactive API Key.")

        # Attach tenant application to request
        request.application = app
        return (AnonymousUser(), app)

    def authenticate_header(self, request) -> str:
        return 'Api-Key realm="ReportForge"'


class APIKeyScheme(OpenApiAuthenticationExtension):
    target_class = "apps.authentication.auth.APIKeyAuthentication"
    name = "ApiKeyAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API Key authentication for ReportForge tenants (e.g. rf_live_...)",
        }
