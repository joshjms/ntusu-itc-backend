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
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema 
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

class OfficerTokenView(APIView):
    def get(self, request, officer_token):
        event_officer = get_objects_or_404(EventOfficer, token=officer_token)
        return JsonResponse(event_officer.event.id)

#JUAN & DEO

#POST /event/<event_id>/create_officer/ (done)
class AddEventOfficer(generics.CreateAPIView):
    querySet = EventOfficer.objects.all()
    serializer_class = EventOfficerSerializer

#GET /event/edit_officer/<officer_token> (done)
class EventOfficerEdit(generics.ListAPIView):
    queryset = EventAdmin.objects.all()
    serializerClass = EventOfficerSerializer
    
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
        if not event.is_open:
            return Response({"detail": "This event is not yet open for check in"}, status=status.HTTP_400_BAD_REQUEST)
        if event.check_in_end_date < date.today():
            return Response({"detail": "Check in for this event has already ended"}, status=status.HTTP_400_BAD_REQUEST)
        event_officer = get_object_or_404(EventOfficer, user=request.user, event=event)
        if not event_officer.is_active:
            return Response({"detail": "You are not currently assigned to any active counter"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            matric_check_in = MatricCheckIn.objects.get(event=event, matric_card=matric_card)
            return Response({"detail": f"Matric card {matric_card} already checked in at counter {matric_check_in.counter}"}, status=status.HTTP_400_BAD_REQUEST)
        except MatricCheckIn.DoesNotExist:
            pass
        serializer = MatricCheckInSerializer(data={"matric_card": matric_card, "event": event.id, "counter": event_officer.counter})
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Matric card successfully checked in"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#GET /event/<event_id>/statistics/
class EventStatistics(APIView):
    def get(self, request, event_id):
        event = Event.objects.get(id=event_id)
        start_date = event.start_date
        end_date = event.end_date
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
            'total_users': event.num_attendees,
            'analytics': analytics
        }

        return Response(response_data)
#GET /event/<event_id>/matric_list/
class MatricList(generics.ListAPIView):
    serializer_class = MatricCheckInSerializer

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        return MatricCheckIn.objects.filter(event_id=event_id)

