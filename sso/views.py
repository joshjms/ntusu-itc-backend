from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import password_validation
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from sso.models import User
from sso.permissions import IsSelfOrReadOnly
from sso.serializers import UserCreateSerializer, UserProfileSerializer


class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = 'username'
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsSelfOrReadOnly]


class UserVerifyView(APIView):
    def get(self, *_, **kwargs):
        user = get_object_or_404(User, custom_token=kwargs['token'])
        user.is_active = True
        user.save()
        return Response({ 'status': 'account activated',})


class UserChangePasswordView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        new_password = request.data.get('new_password', '')
        user = User.objects.get(username=request.user.username)
        try: password_validation.validate_password(new_password, user)
        except ValidationError as errors:
            return Response({ 'errors': errors,}, status=400)
        user.set_password(new_password)
        return Response({ 'status': 'password changed',})
