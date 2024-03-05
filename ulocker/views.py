from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Booking
from .serializers import BookingSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import generics
from rest_framework.response import Response
from .permission import IsULockerAdmin

# GET and POST /ulocker/booking/
class UserBookingListView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)
    
# GET /ulocker/booking/admin/ for admin only
class AdminBookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer
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
    
