from rest_framework import serializers
from event.models import Event, EventAdmin, EventOfficer, MatricCheckIn
from sso.models import User

import random
import string

def generate_token(length=8):
    """
    Generate a random token [A-Z and 0-9] of the specified length.
    """
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))
        
class EventOfficerSerializer(serializers.ModelSerializer):
    added_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    class Meta:
        model = EventOfficer
        fields = ['event', 
                  'name', 
                  'is_active', 
                  'token', 
                  'added_date']
        read_only_fields = ['token', 'added_date', 'event']

    def create(self, validated_data):
        validated_data['token'] = generate_token()
        return EventOfficer.objects.create(**validated_data)

class OfficerLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventOfficer
        fields = ['token']

class MatricListSerializer(serializers.ModelSerializer):
    added_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    class Meta:
        model = MatricCheckIn
        fields = '__all__'
        read_only_fields = ['event', 'officer_name']

class EventSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    end_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    officers = EventOfficerSerializer(many=True)
    matric_checked_in = MatricListSerializer(many=True, read_only=True)
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
                  'auto_end',
                  'officers',
                  'matric_checked_in']
        read_only_fields = ['event_admin', 
                            'auto_start', 
                            'auto_end']

    def create(self, validated_data):
        curr_instance = super().create(validated_data)
        for officer in validated_data.get('officers', []):
            serializer = EventOfficerSerializer(data=officer)
            serializer.is_valid(raise_exception=True)
            serializer.save(event=curr_instance)
        return curr_instance
        

        kwargs = {}
        officer_list = None
        for attr in validated_data.keys():
            val = validated_data.get(attr)
            if val != None:
                if attr == 'officers':
                    officer_list = val
                else:
                    kwargs[attr] = val
        try:
            event = Event.objects.create(**kwargs)
        except: raise Exception("JSON Format is incorrect.")
        if officer_list != None:
            for officer in officer_list:
                serializer = EventOfficerSerializer(data=officer)
                serializer.is_valid(raise_exception=True)
                serializer.save(event=event)
        return event

class MatricCheckInSerializer(serializers.Serializer):
    matric_number = serializers.CharField(required=True, allow_blank=False)
    token = serializers.CharField(required=True, allow_blank=False)
    event = EventSerializer(read_only=True)

    def create(self, validated_data):
        matric_number = validated_data.get('matric_number')
        token = validated_data.get('token')
        officer_name = EventOfficer.objects.get(token=token).name
        event = validated_data.get('event')

        return MatricCheckIn.objects.create(matric_number=matric_number,
                                            officer_name=officer_name,
                                            event=event)

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

class AddEventAdminSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    is_superadmin = serializers.BooleanField()
    user = UserSerializer(read_only=True)

    def create(self, validated_data):
        email = validated_data.get('email')
        user = User.objects.filter(email=email)[:1].get()
        is_superadmin = validated_data.get('is_superadmin')      
        return EventAdmin.objects.create(user=user, is_superadmin=is_superadmin)