from rest_framework import generics
from rest_framework_simplejwt.authentication import JWTAuthentication
from portal.models import UpdateNote, FeedbackForm
from portal.permissions import IsSuperUserOrReadOnly, IsSuperUser
from portal.serializers import (
    UpdateNoteSerializer,
    UpdateNoteSerializerGeneral,
    FeedbackFormUserSerializer,
    FeedbackFormAdminSerializer,
)


class UpdateNoteMixin:
    queryset = UpdateNote.objects.all()
    serializer_class = UpdateNoteSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSuperUserOrReadOnly]


class FeedbackFormMixin:
    queryset = FeedbackForm.objects.all()
    serializer_class = FeedbackFormUserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSuperUser]


class UpdateNoteView(UpdateNoteMixin,
		generics.ListCreateAPIView):
    serializer_class = UpdateNoteSerializerGeneral


class UpdateNoteDetailView(UpdateNoteMixin,
		generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'


class FeedbackView(FeedbackFormMixin,
        generics.ListCreateAPIView):
    def get_permissions(self):
        return (super().get_permissions() if
            self.request.method == 'GET' else [])


class FeedbackDetailView(FeedbackFormMixin,
        generics.RetrieveUpdateAPIView):
    serializer_class = FeedbackFormAdminSerializer
    lookup_field = 'id'
