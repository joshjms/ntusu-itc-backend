from rest_framework import generics
from event.serializers import EventSerializer, EventAdminSerializer, UserSerializer, AddEventAdminSerializer
from event.models import Event, EventAdmin
from event.permissions import IsEventAdmin, IsEventCreator, IsEventSuperAdmin
from sso.models import User
from rest_framework.response import Response
from rest_framework import status

class EventListAll(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsEventSuperAdmin]


class EventList(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsEventAdmin]

    def get_queryset(self):
        event_admin = EventAdmin.objects.get(user=self.request.user)
        return Event.objects.filter(event_admin=event_admin)


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

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Event.objects.filter(pk=pk)

    def perform_update(self, serializer):
        print('peko')
        serializer.save(auto_start=True, auto_end=True)


class AdminList(generics.ListAPIView):
    queryset = EventAdmin.objects.all()
    serializer_class = EventAdminSerializer
    permission_classes = [IsEventSuperAdmin]


class AdminUpdate(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventAdminSerializer
    permission_classes = [IsEventSuperAdmin]
    def get_queryset(self):
        pk = self.kwargs['pk']
        return EventAdmin.objects.filter(pk=pk)
    

class UserList(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsEventSuperAdmin]

    def get_queryset(self):
        list_user_id = list(EventAdmin.objects.values_list('user_id'))
        list_user_id = [id[0] for id in list_user_id]
        return User.objects.exclude(id__in=list_user_id)


class AddEventAdmin(generics.CreateAPIView):
    queryset = EventAdmin.objects.all()
    serializer_class = AddEventAdminSerializer
    permission_classes = [IsEventSuperAdmin]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data,list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)