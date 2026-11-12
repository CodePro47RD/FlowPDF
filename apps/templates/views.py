from rest_framework import viewsets
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Template
from .serializers import TemplateSerializer


@extend_schema_view(
    list=extend_schema(summary="List all templates belonging to authenticated tenant"),
    create=extend_schema(summary="Create a new reusable document template"),
    retrieve=extend_schema(summary="Retrieve template details by ID"),
    update=extend_schema(summary="Update an existing template definition"),
    partial_update=extend_schema(summary="Partially update an existing template"),
    destroy=extend_schema(summary="Delete a template"),
)
class TemplateViewSet(viewsets.ModelViewSet):
    """
    CRUD API for managing tenant-scoped document templates.
    """
    serializer_class = TemplateSerializer

    def get_queryset(self):
        app = getattr(self.request, "application", None)
        if app is not None:
            return Template.objects.filter(application=app)
        if self.request.user and self.request.user.is_staff:
            return Template.objects.all()
        return Template.objects.none()
