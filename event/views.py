from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from event.models import Event, EventAdmin, EventOfficer, MatricCheckIn
from event.serializers import (
    EventSerializer, EventAdminSerializer, UserSerializer, 
    EventOfficerSerializer, MatricCheckInSerializer
)
from event.permissions import (
    IsEventAdmin, IsEventCreator, IsEventSuperAdmin, IsEventOfficer
)
from datetime import date
from datetime import timedelta
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema 
from rest_framework import generics
from event.serializers import EventSerializer, EventAdminSerializer, UserSerializer, AddEventAdminSerializer
from event.models import Event, EventAdmin
from event.permissions import IsEventAdmin, IsEventCreator, IsEventSuperAdmin
from sso.models import User
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.views import APIView
from django.db.models import Count

import random
import string

def generate_token(length=8):
    """
    Generate a random token of the specified length.
    """
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

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

class CheckAdminStatus(APIView):
     def get(self, request):
          if request.user.is_anonymous:
               return Response('Unauthorized', status=status.HTTP_401_UNAUTHORIZED)
          user = User.objects.get(id=request.user.id)
          try:
               event_admin = EventAdmin.objects.get(user=user)
               if event_admin.is_superadmin:
                 return Response('event_superadmin', status=status.HTTP_200_OK)
               else:
                 return Response('event_admin', status=status.HTTP_200_OK)
          except EventAdmin.DoesNotExist:
               return Response('regular_user', status=status.HTTP_200_OK)

#POST /event/<event_id>/create_officer/ (done)
class AddEventOfficer(generics.CreateAPIView):
    serializer_class = EventOfficerSerializer

    def create(self, request, event_id):
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            return Response({"detail": "Invalid event id"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['token'] = generate_token()
            serializer.validated_data['event'] = event
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#GET /event/edit_officer/<officer_token> (done)
class EventOfficerEdit(generics.RetrieveUpdateAPIView):
    queryset = EventOfficer.objects.all()
    serializer_class = EventOfficerSerializer
    permission_classes = [IsAuthenticated, IsEventAdmin]
    
#POST /event/officer_login/  
class EventOfficerLoginView(APIView):
    def post(self, request, format=None):
        token = request.data.get('token')
        try:
            event_officer = EventOfficer.objects.get(token=token)
        except EventOfficer.DoesNotExist:
            return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        event_id = event_officer.event.id
        return Response({"event_id": event_id})

#POST /event/<event_id>/input/
class EventInputView(APIView):
    permission_classes = [IsAuthenticated, IsEventOfficer]

    def post(self, request, event_id, format=None):
        matric_card = request.data.get('matric_card')
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            return Response({"detail": "Invalid event id"}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the event is open for check-in
        if not event.is_active:
            return Response({"detail": "This event is not yet open for check in"}, status=status.HTTP_400_BAD_REQUEST)
      
        # Check if the current officer is assigned to an active counter
        event_officer = get_object_or_404(EventOfficer, user=request.user, event=event)
        if not event_officer.is_active:
            return Response({"detail": "You are not currently assigned to any active counter"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the matric card is valid for the event
        matric_prefix = matric_card[0]
        if event.is_undergraduate_only and not matric_prefix == 'U':
            return Response({"detail": "This event is only open to undergraduate students"}, status=status.HTTP_400_BAD_REQUEST)
        elif not event.is_postgraduate_allowed and matric_prefix == 'P':
            return Response({"detail": "This event is not open to postgraduate students"}, status=status.HTTP_400_BAD_REQUEST)
        elif matric_prefix == 'N':
            return Response({"detail": "Exchange students are not allowed for this event"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the matric card has already checked in for the event
        try:
            matric_check_in = MatricCheckIn.objects.get(event=event, matric_number=matric_card)
            return Response({"detail": f"Matric card {matric_card} already checked in at counter {matric_check_in.officer_name}"}, status=status.HTTP_400_BAD_REQUEST)
        except MatricCheckIn.DoesNotExist:
            pass
        
        # Save the check-in record
        serializer = MatricCheckInSerializer(data={"matric_number": matric_card, "event": event.id, "officer_name": event_officer.name})
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Matric card successfully checked in"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#GET /event/<event_id>/statistics/
class EventStatistics(APIView):
    def get(self, request, event_id):
        event = Event.objects.get(id=event_id)
        start_date = event.start_time
        end_date = event.end_time
        num_days = (end_date - start_date).days + 1

        # Get total number of check-ins for the event
        total_check_ins = MatricCheckIn.objects.filter(event=event).count()

        # Aggregate check-ins by date
        check_ins_by_date = MatricCheckIn.objects \
            .filter(event=event, created_at__date__gte=start_date, created_at__date__lte=end_date) \
            .values('created_at__date') \
            .annotate(check_ins=Count('id')) \
            .order_by('created_at__date')

        # Compute accumulated check-ins
        accumulated_check_ins = 0
        analytics = []
        for i in range(num_days):
            check_ins = 0
            check_ins_date = start_date + timedelta(days=i)
            for item in check_ins_by_date:
                if item['created_at__date'] == check_ins_date:
                    check_ins = item['check_ins']
                    accumulated_check_ins += check_ins
                    break
            analytics.append({
                'date': check_ins_date.strftime('%d-%m-%Y'),
                'check_ins': check_ins,
                'accumulated_check_ins': accumulated_check_ins
            })

        response_data = {
            'total_check_ins': total_check_ins,
            'analytics': analytics
        }

        return Response(response_data)

#GET /event/<event_id>/matric_list/
class MatricList(generics.ListAPIView):
    serializer_class = MatricCheckInSerializer

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        return MatricCheckIn.objects.filter(event_id=event_id)
