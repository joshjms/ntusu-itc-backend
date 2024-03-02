from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Booking
from .serializers import BookingSerializer
from rest_framework.filters import SearchFilter, OrderingFilter

# GET and POST /ulocker/booking/
class UserBookingListView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Booking.objects.filter(user=user)
    
# GET /ulocker/booking/admin/ for admin only
class AdminBookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['applicant_name', 'matric_no', 'organization_name']
    ordering_fields = ['creation_date', 'start_month', 'end_month', 'duration', 'organization_name', 'applicant_name']

    def get_queryset(self):
        queryset = Booking.objects.all()

        for key, value in self.request.query_params.items():
            if key in ['creation_date', 'start_month', 'end_month', 'duration', 'organization_name', 'applicant_name']:
                queryset = queryset.filter(**{key: value})

        return queryset
    

# PUT /ulocker/booking/admin/ for admin only
class ChangeBookingStatusView(generics.UpdateAPIView):
    serializer_class = BookingSerializer
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

        booking.status = status
        booking.save()

        serializer = self.get_serializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)

# PUT /ulocker/change_payment_status/ for admin only
class ChangePaymentStatusView(generics.UpdateAPIView):
    serializer_class = BookingSerializer
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