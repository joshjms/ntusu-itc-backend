from rest_framework import serializers, status
from sso.serializers import UserProfileSerializer
from ufacility.models import Verification, Booking2, Venue, UFacilityUser
from ufacility.utils import clash_exists


class ConflictValidationError(serializers.ValidationError):
    status_code = status.HTTP_409_CONFLICT


class UFacilityUserSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(many=False, read_only=True)
    
    class Meta:
        model = UFacilityUser
        fields = '__all__'
        read_only_fields = ['id', 'user', 'is_admin', 'cca']


class VerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Verification
        fields = '__all__'


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    user = UFacilityUserSerializer(many=False)
    venue = VenueSerializer(many=False)

    class Meta:
        model = Booking2
        fields = '__all__'
        read_only_fields = ['id', 'user', 'status']
    
    def validate(self, attrs):
        if clash_exists(attrs['venue'].id, attrs['start_time'], attrs['end_time']):
            raise ConflictValidationError('Booking clashes with another accepted booking')
        return super().validate(attrs)
