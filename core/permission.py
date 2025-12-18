from rest_framework.permissions import BasePermission

class IsPartner(BasePermission):
    """Allow access only to partners."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'partner')