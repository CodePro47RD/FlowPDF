"""
ReportForge main URL Configuration.
Exposes versioned REST API at /api/v1/ and OpenAPI Swagger docs at /api/docs/.
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from apps.templates.views import TemplateViewSet
from apps.assets.views import AssetViewSet
from apps.reports.views import (
    ReportGenerateView,
    ReportPreviewView,
    ReportDetailView,
    ReportDownloadView,
)

router = DefaultRouter()
router.register(r"templates", TemplateViewSet, basename="template")
router.register(r"assets", AssetViewSet, basename="asset")

v1_patterns = [
    # Reports
    path("reports/generate/", ReportGenerateView.as_view(), name="report-generate"),
    path("reports/preview/", ReportPreviewView.as_view(), name="report-preview"),
    path("reports/<uuid:pk>/", ReportDetailView.as_view(), name="report-detail"),
    path("reports/<uuid:pk>/download/", ReportDownloadView.as_view(), name="report-download"),

    # Router (templates, assets)
    path("", include(router.urls)),
]

urlpatterns = [
    path("admin/", admin.site.urls),

    # API v1
    path("api/v1/", include(v1_patterns)),

    # OpenAPI 3 Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
