from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from portal.models import UpdateNote, FeedbackForm
from portal.utils import send_feedback_submission, send_feedback_reply


class UpdateNoteSerializer(serializers.ModelSerializer):
    added = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    class Meta:
        model = UpdateNote
        fields = ('id', 'title', 'description', 'content', 'added',)


class UpdateNoteSerializerGeneral(UpdateNoteSerializer):
    content = serializers.CharField(write_only=True)


class FeedbackFormUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackForm
        fields = ('id', 'type', 'title', 'details', 'email', 'resolved',)
        read_only_fields = ('resolved',)
    
    def create(self, validated_data):
        # send_feedback_submission('', '') # TODO
        return super().create(validated_data)


class FeedbackFormAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackForm
        fields = ('id', 'type', 'title', 'details', 'email', 'response', 'resolved',)
        read_only_fields = ('id', 'type', 'title', 'details', 'email', 'resolved',)

    def update(self, instance, validated_data):
        if instance.resolved:
            raise ValidationError('Response already given! Only 1 response is allowed!')
        # send_feedback_reply(instance.email, validated_data['response']) TODO
        instance.resolved = True
        return super().update(instance, validated_data)    
