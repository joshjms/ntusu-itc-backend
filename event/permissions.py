from rest_framework import permissions
from event.models import EventAdmin, Event

class IsEventAdmin(permissions.BasePermission):
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
            # bypass permission if event superadmin
            if event_admin.is_superadmin: return True

            if obj.__class__.__name__ == "Event":
                return obj.event_admin == event_admin
            elif obj.__class__.__name__ == "EventOfficer":
                return obj.event.event_admin == event_admin
        except:
            return False

class IsEventSuperAdmin(permissions.BasePermission):
    message = 'You are not an Event SuperAdmin.'
    def has_permission(self, request, view):
        try:
            event_admin = EventAdmin.objects.get(user=request.user)
            return event_admin.is_superadmin
        except:
            return False

class IsEventCreatorPK(permissions.BasePermission):
    message = 'You are not the creator of this event.'
    def has_permission(self, request, view):
        try:
            event_admin = EventAdmin.objects.get(user=request.user)
            # bypass permission if event superadmin
            if event_admin.is_superadmin: return True
            event = Event.objects.get(pk=view.kwargs['pk'])
            return event.event_admin == event_admin
        except:
            return False