from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Booking
from rest_framework import status
from .serializers import BookingPartialSerializer, BookingCompleteSerializer, BookingStatusSerializer
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
        statusName = request.data.get('status')
        print(statusName)

        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({"error": "Booking with this ID does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(booking, data={'status': statusName}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_200_OK)

# PUT /ulocker/change_payment_status/ for admin only
class ChangePaymentStatusView(generics.UpdateAPIView):
    serializer_class = BookingPartialSerializer
    permission_classes = [IsAdminUser]

    def update(self, request, *args, **kwargs):
        booking_id = request.data.get('booking_id')
        status = request.data.get('status')

        if not booking_id or not status:
            return Response({'error': 'Booking ID and status are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)

        booking.payment_status = status
        booking.save()

        serializer = self.get_serializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)