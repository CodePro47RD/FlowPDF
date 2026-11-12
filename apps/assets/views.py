from rest_framework import viewsets, parsers
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Asset
from .serializers import AssetSerializer


@extend_schema_view(
    list=extend_schema(summary="List uploaded assets for tenant"),
    create=extend_schema(summary="Upload a new image or font asset"),
    retrieve=extend_schema(summary="Get asset details"),
    destroy=extend_schema(summary="Delete an asset"),
)
class AssetViewSet(viewsets.ModelViewSet):
    serializer_class = AssetSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    http_method_names = ["get", "post", "delete"]

    def get_queryset(self):
        app = getattr(self.request, "application", None)
        if app is not None:
            return Asset.objects.filter(application=app)
        if self.request.user and self.request.user.is_staff:
            return Asset.objects.all()
        return Asset.objects.none()
