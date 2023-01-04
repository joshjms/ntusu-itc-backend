from rest_framework import serializers
from starswar.models import CourseIndex, SwapRequest


class CourseIndexPartialSerializer(serializers.ModelSerializer):
    datetime_added = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    class Meta:
        model = CourseIndex
        fields = ('id', 'code', 'name', 'index', 'datetime_added', 'pending_count',)


class CourseIndexCompleteSerializer(serializers.ModelSerializer):
    datetime_added = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    class Meta:
        model = CourseIndex
        fields = ('id', 'code', 'name', 'index', 'datetime_added', 'pending_count', 'information',)
        read_only_fields = ('id', 'datetime_added', 'pending_count',)
