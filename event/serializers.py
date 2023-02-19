from rest_framework import serializers
from event.models import Event, EventAdmin, EventOfficer, MatricCheckIn
from sso.models import User

import random
import string

def generate_token(length=8):
    """
    Generate a random token of the specified length.
    """
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

class EventSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    end_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    class Meta:
        model = Event
        fields = ['id',
                  'name', 
                  'is_active', 
                  'allow_non_undergraduate', 
                  'allow_exchange_student',
                  'event_admin',
                  'start_time',
                  'end_time', 
                  'auto_start',
                  'auto_end']
        read_only_fields = ['event_admin', 
                            'auto_start', 
                            'auto_end']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 
                  'email', 
                  'id', 
                  'display_name']
        read_only_fields = ['username', 
                            'email', 
                            'id', 
                            'display_name']

class EventAdminSerializer(serializers.ModelSerializer):
    events = EventSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    class Meta:
        model = EventAdmin
        fields = '__all__'

class EventOfficerSerializer(serializers.ModelSerializer):
    events = EventSerializer(many=True, read_only=True)

    class Meta:
        model = EventOfficer
        fields = ['event', 'name', 'is_active', 'token', 'added_date']
        read_only_fields = ['token', 'added_date']

    def create(self, validated_data):
        validated_data['token'] = generate_token()
        return EventOfficer.objects.create(validated_data)

class MatricCheckInSerializer(serializers.ModelSerializer):
    events = EventSerializer(many=True, read_only=True)
    class Meta:
        model = MatricCheckIn
        fields = '__all__'

class AddEventAdminSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    is_superadmin = serializers.BooleanField()
    user = UserSerializer(read_only=True)

    def create(self, validated_data):
        email = validated_data.get('email')
        user = User.objects.filter(email=email)[:1].get()
        is_superadmin = validated_data.get('is_superadmin')      
        return EventAdmin.objects.create(user=user, is_superadmin=is_superadmin)
