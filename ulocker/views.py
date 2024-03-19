from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Booking, Location, Locker
from rest_framework import status
from .serializers import BookingPartialSerializer, BookingCompleteSerializer, BookingStatusSerializer, PaymentStatusSerializer, LocationListSerializer, LockerListSerializer, LockerStatusListSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import generics
from rest_framework.response import Response
from .permission import IsULockerAdmin
from rest_framework.response import Response

# GET and POST /ulocker/booking/
class UserBookingListView(generics.ListCreateAPIView):
    serializer_class = BookingPartialSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)
    
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

# PUT /ulocker/change_payment_status/ for admin only
class ChangePaymentStatusView(generics.UpdateAPIView):
    serializer_class = PaymentStatusSerializer
    permission_classes = [IsULockerAdmin]

    def update(self, request, *args, **kwargs):
        booking_id = request.data.get('booking_id')
        payment_status = request.data.get('payment_status')

        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({"error": "Booking with this ID does not exist."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(booking, data={'payment_status': payment_status}, partial=True)
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

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.validators import RegexValidator

validate_date_format = RegexValidator(
    regex=r'^(0[1-9]|1[0-2])/\d{4}$',
    message="Invalid date format. Date must be MM/YYYY format"
)

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
        return super().get(request, *args, **kwargs)

    def calculate_end_month(self, start_month, duration):
        start_month = start_month.split('/')
        month = int(start_month[0])
        year = int(start_month[1])
        duration = int(duration)
        month += duration
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

    def get_queryset(self):
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
            
            # filter the bookings for this locker within the start_month and duration
            for booking in bookings:
                if booking.locker == locker and self.check_overlap(booking.start_month, booking.duration, start_month, duration):
                    locker.status = booking.status
                    break

        return queryset