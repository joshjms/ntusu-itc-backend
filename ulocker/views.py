from rest_framework import generics, status
from rest_framework import generics
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import Booking, Location, Locker, validate_date_format
from .permission import IsULockerAdmin
from .serializers import (
    BookingPartialSerializer,
    BookingCompleteSerializer,
    BookingStatusSerializer,
    LocationListSerializer,
    LockerListSerializer,
    LockerStatusListSerializer,
)


# GET and POST /ulocker/booking/
class UserBookingListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        return BookingPartialSerializer if self.request.method == 'POST' else BookingCompleteSerializer
    
# GET /ulocker/booking/admin/ for admin only
class AdminBookingListView(generics.ListAPIView):
    serializer_class = BookingCompleteSerializer
    permission_classes = [IsULockerAdmin]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['applicant_name', 'matric_no', 'organization_name']
    ordering_fields = ['creation_date', 'start_month', 'end_month', 'duration', 'organization_name', 'applicant_name']

    def get_queryset(self):
        queryset = Booking.objects.all()

        for key, value in self.request.query_params.items():
            if key in ['creation_date', 'start_month', 'end_month', 'duration', 'organization_name', 'applicant_name']:
                queryset = queryset.filter(**{key: value})

        return queryset

# PUT /ulocker/change_booking_status/ for admin only
class ChangeBookingStatusView(generics.UpdateAPIView):
    serializer_class = BookingStatusSerializer
    permission_classes = [IsULockerAdmin]

    def update(self, request, *args, **kwargs):
        booking_id = request.data.get('booking_id')
        status_name = request.data.get('status')

        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({"error": "Booking with this ID does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(booking, data={'status': status_name}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_200_OK)

# GET /ulocker/location/
class LocationListView(generics.ListAPIView):
    serializer_class = LocationListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Location.objects.all()

        for key, value in self.request.query_params.items():
            if key in ['id']:
                queryset = queryset.filter(**{key: value})

        return queryset
    
# Get /ulocker/locker/<int: location_id>/
class LockerListView(generics.ListAPIView):
    serializer_class = LockerListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Locker.objects.all()

        location_id = self.kwargs.get('location_id')
        if location_id is not None:
            return queryset.filter(location_id=location_id)  

        return queryset

#GET /ulocker/locker/?location_id=<int>&start_month=<int>&duration=<int> 
class isBookedListView(generics.ListAPIView):
    serializer_class = LockerStatusListSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('location_id', openapi.IN_QUERY, description="Location ID", type=openapi.TYPE_INTEGER),
        openapi.Parameter('start_month', openapi.IN_QUERY, description="Start Month", type=openapi.TYPE_STRING),
        openapi.Parameter('duration', openapi.IN_QUERY, description="Duration", type=openapi.TYPE_INTEGER),
    ])
    def get(self, request, *args, **kwargs):
        bookings = Booking.objects.all()
        location_id = self.request.query_params.get('location_id', None)
        start_month = self.request.query_params.get('start_month', None)
        duration = self.request.query_params.get('duration', None)
        if location_id is None or start_month is None or duration is None:
            return Response({"error": "location_id, start_month and duration are required."}, status=status.HTTP_400_BAD_REQUEST)
        validate_date_format(start_month)

        # filter by location
        queryset = Locker.objects.filter(location_id=location_id)

        # add status to each locker
        for locker in queryset:
            
            locker.status = 'unused'
            if locker.is_available == False:
                locker.status = 'not available'
                continue
            
            # filter the bookings for this locker within the start_month and duration
            status_number_map = {
                0: 'available',
                1: 'reserved',
                2: 'occupied'
            }
            for booking in bookings:
                
                status_number = 0
                if self.check_overlap(booking.start_month, booking.duration, start_month, duration):
                    if booking.status in ['allocated']:
                        status_number = max(status_number, 2)
                    elif booking.status in ['pending', 'approved - awaiting payment', 'approved - awaiting verification']:
                        status_number = max(status_number, 1)
                    else:
                        status_number = max(status_number, 0)
                        
                locker.status = status_number_map[status_number]
                
        return Response(LockerStatusListSerializer(queryset, many=True).data)

    def calculate_end_month(self, start_month, duration):
        start_month = start_month.split('/')
        month = int(start_month[0])
        year = int(start_month[1])
        duration = int(duration)
        month += duration - 1
        while month > 12:
            month -= 12
            year += 1
        return f"{month:02d}/{year}"

    def check_overlap(self, start_month1, duration1, start_month2, duration2):
        end_month1 = self.calculate_end_month(start_month1, duration1)
        end_month2 = self.calculate_end_month(start_month2, duration2)
        if start_month1 == start_month2 or end_month1 == end_month2:
            return True
        if start_month1 < start_month2:
            return end_month1 >= start_month2
        else:
            return end_month2 >= start_month1
