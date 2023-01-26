from rest_framework import generics
from event.serializers import EventSerializer, EventAdminSerializer, UserSerializer
from event.models import Event, EventAdmin
from event.permissions import IsEventAdmin, IsEventCreator, IsEventSuperAdmin
from sso.models import User



class EventListAll(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsEventSuperAdmin]

class EventList(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsEventAdmin]
#     def get_queryset(self):
#         event_admin = EventAdmin.objects.get(user=self.request.user)
#         return Event.objects.filter(event_admin=event_admin)

class EventCreate(generics.CreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsEventAdmin]
    def perform_create(self, serializer):
        user = self.request.user
        event_admin = EventAdmin.objects.get(user=user)
        serializer.save(event_admin=event_admin)

class EventEdit(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsEventCreator]
#     def get_queryset(self):
#         pk = self.kwargs['pk']
#         return Event.objects.filter(pk=pk)



class AdminList(generics.ListAPIView):
    queryset = EventAdmin.objects.all()
    serializer_class = EventAdminSerializer
    permission_classes = [IsEventSuperAdmin]

class AdminUpdate(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventAdminSerializer
    permission_classes = [IsEventSuperAdmin]
#     def get_queryset(self):
#         pk = self.kwargs['pk']
#         return EventAdmin.objects.filter(pk=pk)
    
class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsEventSuperAdmin]
