from rest_framework import permissions
from ufacility.models import UFacilityUser


class IsAuthenticated(permissions.IsAuthenticated):
    pass


class IsUFacilityUser(IsAuthenticated):
    message = 'UFacility User Required'

    def has_permission(self, request, view):
        if super().has_permission(request, view):
            try:
                UFacilityUser.objects.get(user=request.user)
                return True
            except UFacilityUser.DoesNotExist:
                return False
        return False


class IsUFacilityAdmin(IsUFacilityUser):
    message = 'UFacility Admin Required'

    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return UFacilityUser.objects.get(user=request.user).is_admin
        return False


class IsInstanceOwnerOrAdmin(IsAuthenticated):
    message = 'Owner of this Instance or UFacility Admin Required'

    def has_object_permission(self, request, view, obj):
        try:
            ufacility_user = UFacilityUser.objects.get(user=request.user)
            return ufacility_user.is_admin or obj.user == ufacility_user
        except UFacilityUser.DoesNotExist:
            return False


class IsPendingBookingOrAdmin(permissions.BasePermission):
    message = 'Editing and deleting is only allowed for pending bookings or UFacility Admin Required'

    def has_object_permission(self, request, view, obj):
        if obj.status == 'pending':
            return True
        ufacility_user = UFacilityUser.objects.get(user=request.user)
        return ufacility_user.is_admin
