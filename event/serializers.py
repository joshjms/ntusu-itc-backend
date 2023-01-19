from rest_framework import serializers
from event.models import Event, EventAdmin
from sso.models import User

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['event_admin']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'id']
        read_only_fields = ['username', 'email', 'id']

class EventAdminSerializer(serializers.ModelSerializer):
    events = EventSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    class Meta:
        model = EventAdmin
        fields = '__all__'