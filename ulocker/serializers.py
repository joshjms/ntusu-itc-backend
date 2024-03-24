from rest_framework import serializers
from .models import Booking, Location, Locker

class BookingCompleteSerializer(serializers.ModelSerializer):
    locker_name = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Booking
        fields = '__all__'
        
    def get_locker_name(self, obj):
        return obj.locker.name

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

class LocationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class LockerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Locker
        fields = '__all__'

class LockerStatusListSerializer(serializers.ModelSerializer):
    status = serializers.CharField()

    class Meta:
        model = Locker
        fields = '__all__'
        extra_fields = ['status']