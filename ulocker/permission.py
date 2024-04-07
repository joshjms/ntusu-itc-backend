from .models import ULockerAdmin
from rest_framework.permissions import IsAuthenticated


class IsULockerAdmin(IsAuthenticated):
    message = 'ULocker Admin Required'

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        try:
            return ULockerAdmin.objects.get(user=request.user)
        except ULockerAdmin.DoesNotExist:
            return False
