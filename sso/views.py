from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.generics import get_object_or_404
from django.contrib.auth import password_validation, hashers
from django.core.exceptions import ValidationError
from django.utils import timezone as tz
from django.utils.crypto import get_random_string
from datetime import timedelta as td
from portal.permissions import IsSelfOrReadOnly
from sso.models import User
from sso.serializers import (
    UserCreateSerializer,
    UserProfileSerializer,
    EmailSerializer,
    TokenSerializer,
    PasswordResetSerializer,
)
from sso.utils import send_reset_token


class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = 'username'
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSelfOrReadOnly]


class UserVerifyView(APIView):
    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        user = get_object_or_404(User, custom_token=token)
        user.is_active = True
        user.save()
        return Response({ 'status': 'account activated',})


class ChangePasswordView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def put(self, request):
        current_password = request.data.get('current_password', '')
        print(current_password)
        new_password = request.data.get('new_password', '')
        user = User.objects.get(username=request.user.username)
        try:
            valid = user.check_password(current_password)
            if not valid:
                raise ValidationError('password does not match current')
            password_validation.validate_password(new_password, user)
        except ValidationError as errors:
            return Response({ 'errors': errors,}, status=400)
        user.set_password(new_password)
        user.save()
        return Response({ 'status': 'password changed',})


class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email'].lower()
        user = get_object_or_404(User, email=email)
        if not user.custom_token or not user.token_expiry_date or\
                user.token_expiry_date > tz.now():
            user.custom_token = get_random_string(20)
        user.token_expiry_date = tz.now() + td(days=1)
        user.save()
        send_reset_token(user.email, user.custom_token, user.username)
        return Response({ 'status': 'ok',})


class ResetPasswordView(APIView):
    def put(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(custom_token=
                                serializer.validated_data['token'])
        pw = serializer.validated_data['password']
        user.password = hashers.make_password(pw)
        user.is_active = True
        user.token_expiry_date = tz.now()
        user.save()
        return Response({ 'status': 'ok',})


class TokenCheckView(APIView):
    def get(self, _, token):
        user = get_object_or_404(User, custom_token=token)
        print("TEST")
        print(user.token_expiry_date)
        print(tz.now())
        if tz.now() > user.token_expiry_date:
            return Response({ 'status': 'token expired', },
                status=status.HTTP_401_UNAUTHORIZED)
        return Response({ 'status': 'token valid', },
            status=status.HTTP_200_OK)
