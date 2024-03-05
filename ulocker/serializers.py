from rest_framework import serializers
from .models import Booking

class BookingCompleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

class BookingPartialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['locker', 'applicant_name', 'matric_no', 'phone_no', 'organization_name', 'position', 'start_month', 'duration']

class BookingStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['status']
        extra_fields = ['booking_id']

class PaymentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['payment_status']
        extra_fields = ['booking_id']
