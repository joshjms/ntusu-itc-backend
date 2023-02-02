from rest_framework import serializers, status
from sso.serializers import UserProfileSerializer
from ufacility.models import Verification, Booking2, Venue, UFacilityUser
from ufacility.utils import clash_exists
from ufacility import utils


class ConflictValidationError(serializers.ValidationError):
    status_code = status.HTTP_409_CONFLICT


class UFacilityUserSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(many=False, read_only=True)
    
    class Meta:
        model = UFacilityUser
        fields = '__all__'
        read_only_fields = ['id', 'user', 'is_admin', 'cca']


class VerificationSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(many=False, read_only=True)

    class Meta:
        model = Verification
        fields = '__all__'
        read_only_fields = ['id', 'user', 'status']
    
    def create(self, validated_data):
        validated_data['status'] = 'pending'
        utils.send_verification_email_to_admins()
        return super().create(validated_data)


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    user = UFacilityUserSerializer(many=False, read_only=True)

    class Meta:
        model = Booking2
        fields = '__all__'
        read_only_fields = ['id', 'user', 'status']
    
    def validate(self, attrs):
        if clash_exists(attrs['venue'].id, attrs['date'], attrs['start_time'], attrs['end_time']):
            raise ConflictValidationError('Booking clashes with another accepted booking')
        return super().validate(attrs)
    
    def create(self, validated_data):
        utils.send_booking_email_to_admins()
        validated_data['status'] = 'pending'
        super().create(validated_data)


class BookingReadSerializer(BookingSerializer):
    venue = VenueSerializer(many=False, read_only=True)
