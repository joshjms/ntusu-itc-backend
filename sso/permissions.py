from rest_framework.permissions import BasePermission


class IsSelfOrReadOnly(BasePermission):
    def has_object_permission(self, request, _, obj):
        return bool(
            request.method == 'GET' or
            request.user == obj
        )
