from rest_framework import serializers
from django.utils import timezone as tz
from sso.serializers import UserProfileSerializer
from ufacility.models import Verification, Booking2, Venue, UFacilityUser, BookingGroup, SecurityEmail
from datetime import timedelta
from ufacility.utils.algo import clash_exists
from ufacility.utils import email


class BookingSerializer(serializers.ModelSerializer): # TODO - delete this later
    class Meta:
        model = Booking2
        fields = '__all__'

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
        email.send_verification_email_to_admins()
        return super().create(validated_data)


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = '__all__'


class SecurityEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityEmail
        fields = '__all__'


class BookingPartialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking2
        fields = ['user_email', 'user_cca', 'date', 'start_time', 'end_time', 'purpose', 'pax', 'status']
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
    
    def serialize_to_booking(self, date):
        return {
            'user': UFacilityUser.objects.get(id=self.data['user']),
            'venue': Venue.objects.get(id=self.data['venue']),
            'start_time': self.data['start_time'],
            'end_time': self.data['end_time'],
            'purpose': self.data['purpose'],
            'pax': self.data['pax'],
            'status': 'pending',
            'date': date,
            'booking_group': self.instance,
        }
    
    def accept_booking_group(self):
        booking_group = self.instance
        booking_group.status = 'accepted'
        booking_group.save()
        for booking in booking_group.bookings.all():
            booking.status = 'accepted'
            booking.save()
        email.send_email_to_security(booking_group.venue, booking_group.start_time, booking_group.end_time)
        user = booking_group.user.user
        email.send_booking_results_email(user.email, booking_group.venue, booking_group.start_time, booking_group.end_time, booking_group.status)
    
    def reject_booking_group(self):
        booking_group = self.instance
        booking_group.status = 'declined'
        booking_group.save()
        for booking in booking_group.bookings.all():
            booking.status = 'declined'
            booking.save()
        user = booking_group.user.user
        email.send_booking_results_email(user.email, booking_group.venue, booking_group.start_time, booking_group.end_time, booking_group.status)

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

    def validate_end_date(self, value):
        if value > tz.now().date() + timedelta(days=180):
            raise serializers.ValidationError('You can only book up to 180 days ahead of today')
        return value
    
    def validate(self, attrs):
        if attrs['start_date'] > attrs['end_date']:
            raise serializers.ValidationError('Start date cannot be later than end date')
        if attrs['start_time'] >= attrs['end_time']:
            raise serializers.ValidationError('Start time cannot be the same or later than end time')
        if len(BookingGroup.get_dates(attrs['recurring'], attrs['start_date'], attrs['end_date'])) == 0:
            raise serializers.ValidationError('At least one date is needed')
        # TODO - validate clashing
        return super().validate(attrs)
