from rest_framework import serializers
from .models import Booking

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['locker', 'applicant_name', 'matric_no', 'phone_no', 'organization_name', 'position', 'start_month', 'duration']
