from rest_framework.permissions import BasePermission


class IsSelfOrReadOnly(BasePermission):
    def has_object_permission(self, request, _, obj):
        return bool(
            request.method == 'GET' or
            request.user == obj
        )


class IsSuperUserOrReadOnly(BasePermission):
    def has_permission(self, request, _):
        return bool(
            request.method == 'GET' or
            request.user and
            request.user.is_superuser
        )
