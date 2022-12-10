from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from sso.models import User
from sso.permissions import IsSelfOrReadOnly
from sso.serializers import (
    UserCreateSerializer, UserProfileSerializer
)


class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = 'username'
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsSelfOrReadOnly]
