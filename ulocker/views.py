from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Booking
from .serializers import BookingSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import generics
from rest_framework.response import Response

# GET and POST /ulocker/booking/
class UserBookingListView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)
    
