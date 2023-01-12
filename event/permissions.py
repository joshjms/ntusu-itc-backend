from rest_framework import permissions
from event.models import EventAdmin

class IsEventAdmin(permissions.IsAuthenticated):
    message = 'You are not an Event Admin.'
    def has_permission(self, request, view):
        try:
            event_admin = EventAdmin.objects.get(user=request.user)
            return True
        except:
            return False

class IsEventCreator(permissions.IsAuthenticated):
    message = 'You are not the creator of this event.'
    def has_object_permission(self, request, view, obj):
        try:
            event_admin = EventAdmin.objects.get(user=request.user)
            if event_admin.is_superadmin:
                return True
            return obj.event_admin == event_admin
        except:
            return False

class IsEventSuperAdmin(permissions.IsAuthenticated):
    message = 'You are not an Event SuperAdmin.'
    def has_permission(self, request, view):
        try:
            event_admin = EventAdmin.objects.get(user=request.user)
            return event_admin.is_superadmin
        except:
            return False