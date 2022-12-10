from rest_framework import serializers
from portal.models import UpdateNote


class UpdateNoteSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    class Meta:
        model = UpdateNote
        fields = ('title', 'description', 'content', 'date')
