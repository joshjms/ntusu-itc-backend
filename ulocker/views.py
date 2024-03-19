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

    
#GET /ulocker/locker/?location_id=<int>&start_month=<int>&duration=<int> 
class isBookedListView(generics.ListAPIView):
    serializer_class = LockerStatusListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Locker.objects.all()

        location_id = self.kwargs.get('location_id', None)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id) 

        bookings_allocated = Booking.objects.filter(status='allocated')
        bookings_pending = Booking.objects.filter(status='pending')
        lockers_allocated = set([booking.locker for booking in bookings_allocated])
        lockers_pending = set([booking.locker for booking in bookings_pending])
        lockers_used = lockers_allocated.union(lockers_pending)
        lockers_unused = Locker.objects.exclude(id__in=[locker.id for locker in lockers_used])
        
        print(lockers_allocated)
        print(lockers_pending)
        print(lockers_unused)
        
        return queryset


