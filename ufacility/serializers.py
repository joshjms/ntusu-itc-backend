from rest_framework import serializers, status
from django.utils import timezone as tz
from sso.serializers import UserProfileSerializer
from ufacility.models import Verification, Booking2, Venue, UFacilityUser, BookingGroup
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

    def update(self, instance, validated_data):
        instance.cca = validated_data.get("cca", instance.cca)
        instance.hongen_name = validated_data.get("hongen_name", instance.hongen_name)
        instance.hongen_phone_number = validated_data.get("hongen_phone_number", instance.hongen_phone_number)
        instance.status = validated_data.get("status", instance.status)
        instance.save()
        return instance


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    user = UFacilityUserSerializer(many=False, read_only=True)

    class Meta:
        model = Booking2
        fields = '__all__'
        read_only_fields = ['id', 'user', 'status', 'get_clashing_booking_id']
    
    def validate(self, attrs):
        if clash_exists(attrs['venue'].id, attrs['date'], attrs['start_time'], attrs['end_time']):
            raise ConflictValidationError('Booking clashes with another accepted booking')
        return super().validate(attrs)
    
    def create(self, validated_data):
        utils.send_booking_email_to_admins()
        validated_data['status'] = 'pending'
        return super().create(validated_data)


class BookingReadSerializer(BookingSerializer):
    venue = VenueSerializer(many=False, read_only=True)


class BookingPartialSerializer(serializers.ModelSerializer):
    user = UFacilityUserSerializer(many=False, read_only=True)

    class Meta:
        model = Booking2
        fields = ['user', 'start_time', 'end_time', 'purpose', 'pax', 'status']
        read_only_fields = ['user', 'status']


class BookingGroupSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = BookingGroup
        fields = '__all__'
        extra_fields = ['dates', 'venue_name', 'user_email', 'user_cca', 'bookings']
        read_only_fields = ['id', 'user', 'status', 'bookings']
    
    def get_field_names(self, declared_fields, info):
        return super().get_field_names(declared_fields, info) + self.Meta.extra_fields
    
    def create(self, validated_data):
        validated_data['status'] = 'pending'
        return super().create(validated_data)
    
    def validate_start_time(self, value):
        if value.minute != 0:
            raise serializers.ValidationError('Start time minute should be 00')
        return value
    
    def validate_end_time(self, value):
        if value.minute != 0:
            raise serializers.ValidationError('Start time minute should be 00')
        return value
    
    def validate_start_date(self, value):
        if value < tz.now().date():
            raise serializers.ValidationError('Start date cannot be in the past')
        return value
    
    def validate(self, attrs):
        if attrs['start_date'] > attrs['end_date']:
            raise serializers.ValidationError('Start date cannot be later than end date')
        # TODO - validate clashing
        return super().validate(attrs)
