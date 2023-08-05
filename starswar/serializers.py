from rest_framework import serializers
from collections import defaultdict
from starswar.models import XCourseIndex as CourseIndex, XSwapRequest as SwapRequest


class XCourseIndexPartialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseIndex
        fields = ('id', 'code', 'name', 'index', 'pending_count',)


class XCourseIndexCompleteSerializer(serializers.ModelSerializer):
    datetime_added = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    information = serializers.CharField(write_only=True)
    information_data = serializers.SerializerMethodField(read_only=True)
    pending_data = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CourseIndex
        fields = ('id', 'code', 'name', 'index', 'datetime_added',
            'pending_count', 'information', 'information_data', 'pending_data')
        read_only_fields = ('id', 'datetime_added', 'pending_count',)
    
    def get_information_data(self, obj):
        try:
            return obj.get_information
        except IndexError or Exception:
            return 'invalid data format'
    
    def get_pending_data(self, obj):
        resp_dict = defaultdict(int)
        for sr in SwapRequest.objects.all():
            curr_index = sr.current_index.index
            for index in sr.get_wanted_indexes:
                if obj.index == index:
                    resp_dict[curr_index] += 1
        return resp_dict


class XSwapRequestSerializer(serializers.ModelSerializer):
    current_index = serializers.CharField(max_length=5)

    class Meta:
        model = SwapRequest
        fields = ('contact_info', 'current_index', 'get_wanted_indexes',)
    
    def create(self, validated_data):
        from django.shortcuts import get_object_or_404
        validated_data['current_index'] = get_object_or_404(CourseIndex,
            index=validated_data['current_index'])
        return super().create(validated_data)
    
    # def validate_current_index(self, value):
    #     return False
    #     return bool(CourseIndex.objects.filter(index=value).count)
    
    # def validate(self, attrs):
    #     return False
    #     return CourseIndex.objects.filter(index=attrs['current_index']).count() == 1
    
    # def create(self, validated_data):
    #     curr_index = validated_data['current_index']
    #     validated_data['current_index'] = CourseIndex.objects.get(index=curr_index)
    #     return super().create(self, validated_data)
