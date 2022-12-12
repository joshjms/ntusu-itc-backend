from rest_framework import serializers
from portal.models import UpdateNote


class UpdateNoteSerializer(serializers.ModelSerializer):
    added = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    class Meta:
        model = UpdateNote
        fields = ('id', 'title', 'description', 'content', 'added')
