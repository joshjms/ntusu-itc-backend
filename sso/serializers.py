from rest_framework import serializers
from django.contrib.auth import password_validation
from django.utils.crypto import get_random_string
from sso.models import User
from sso.utils import send_activation_token


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['display_name', 'email', 'password',]
    
    def validate_email(self, value):
        if value[value.find('@'):].lower() != '@e.ntu.edu.sg':
            raise serializers.ValidationError('NTU email required')
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('No duplicate email')
        return value

    def validate(self, data):
        user = User(**data)
        password_validation.validate_password(data['password'], user)
        return super().validate(data)
    
    def create(self, validated_data):
        email = validated_data['email']
        validated_data['is_active'] = False
        validated_data['username'] = email[:email.find('@')].lower()
        validated_data['custom_token'] = get_random_string(20)
        send_activation_token(email, validated_data['custom_token'])
        return super().create(validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'display_name', 'description',]
