from portal.mixins import CompleteAPIView
from portal.models import UpdateNote
from portal.serializers import UpdateNoteSerializer


class UpdateNoteView(CompleteAPIView):
    queryset = UpdateNote.objects.all()
    serializer_class = UpdateNoteSerializer
    # authentication_classes = [JWTAuthentication] TODO
    # permission_classes = [IsSelfOrReadOnly] TODO
