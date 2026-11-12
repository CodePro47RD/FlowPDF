from rest_framework import permissions


class HasValidAPIKey(permissions.BasePermission):
    """
    Allows access only to authenticated Applications (or staff users).
    """

    def has_permission(self, request, view) -> bool:
        if getattr(request, "application", None) is not None:
            return True
        if request.user and request.user.is_authenticated and request.user.is_staff:
            return True
        return False
