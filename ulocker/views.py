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
        # Filter bookings based on the current user
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
            if key in ['applicant_name', 'matric_no', 'organization_name', 'position', 'payment_status', 'status', 'start_month', 'end_month']:
                queryset = queryset.filter(**{key: value})

        return queryset
    


    



