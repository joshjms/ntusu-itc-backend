from rest_framework import permissions
from ufacility.models import UFacilityUser


class IsUFacilityUser(permissions.BasePermission):
    message = 'UFacility User Required'

    def has_permission(self, request, view):
        try:
            UFacilityUser.objects.get(user=request.user)
            return True
        except UFacilityUser.DoesNotExist:
            return False
