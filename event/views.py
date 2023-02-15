from django.shortcuts import render

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema 
from django.shortcuts import get_object_or_404


from event.serializers import EventSerializer, EventAdminSerializer, UserSerializer, EventOfficerSerializer, MatricCheckInSerializer
from event.models import Event, EventAdmin, EventOfficer, MatricCheckIn
from event.permissions import IsEventAdmin, IsEventCreator, IsEventSuperAdmin
from sso.models import User



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
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsEventSuperAdmin]


class AddEventOfficer(generics.CreateAPIView):
    querySet = EventOfficer.objects.all()
    serializer_class = EventOfficerSerializer

class EventOfficerEdit(generics.ListAPIView):
    queryset = EventAdmin.objects.all()
    serializerClass = EventOfficerSerializer
    
class OfficerTokenView(APIView):
    def get(request, officer_token):
        event_officer = get_objects_or_404(EventOfficer, token=officer_token)
        return JsonResponse(event_officer.event.id)