from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from django.contrib.auth import password_validation, hashers
from django.utils.crypto import get_random_string
from django.utils import timezone as tz
from sso.models import User
from sso.utils import send_activation_token


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, style={'input_type': 'password'}
    )
    class Meta:
        model = User
        fields = ['display_name', 'email', 'password',]
    
    def validate_email(self, value):
        if value[value.find('@'):].lower() != '@e.ntu.edu.sg':
            raise serializers.ValidationError('NTU email required')
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('No duplicate email')
        return value

    def validate(self, attrs):
        user = User(**attrs)
        password_validation.validate_password(attrs['password'], user)
        return super().validate(attrs)
    
    def create(self, validated_data):
        email, pw = validated_data['email'], validated_data['password']
        validated_data['password'] = hashers.make_password(pw)
        validated_data['is_active'] = False
        validated_data['username'] = email[:email.find('@')].lower()
        validated_data['custom_token'] = get_random_string(20)
        send_activation_token(email, validated_data['custom_token'])
        return super().create(validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'display_name', 'description',]
        read_only_fields = ['id', 'username', 'email',]


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=20)


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=20)
    password = serializers.CharField(
        write_only=True, style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        user = get_object_or_404(User, custom_token=attrs['token'])
        if tz.now() > user.token_expiry_date:
            raise serializers.ValidationError('token already used')
        password_validation.validate_password(attrs['password'], user)
        return super().validate(attrs)
