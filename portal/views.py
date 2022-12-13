from rest_framework import generics
from rest_framework_simplejwt.authentication import JWTAuthentication
from portal.models import UpdateNote
from portal.permissions import IsSuperUserOrReadOnly
from portal.serializers import (
    UpdateNoteSerializer,
    UpdateNoteSerializerGeneral
)


class UpdateNoteMixin:
    queryset = UpdateNote.objects.all()
    serializer_class = UpdateNoteSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSuperUserOrReadOnly]


class UpdateNoteView(UpdateNoteMixin,
		generics.ListCreateAPIView):
    serializer_class = UpdateNoteSerializerGeneral


class UpdateNoteDetailView(UpdateNoteMixin,
		generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'
