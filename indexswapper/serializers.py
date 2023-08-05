import os
from collections import defaultdict
from django.core.validators import MinLengthValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from indexswapper.models import CourseIndex, SwapRequest
from indexswapper.utils.decorator import lock_db_table
from indexswapper.utils.scraper import populate_modules
from indexswapper.utils.validation import ConflictValidationError


MAX_SWAPREQUESTS_PER_USER = 8


class PopulateDatabaseSerializer(serializers.Serializer):
    admin_key = serializers.CharField(max_length=100)
    web_link = serializers.CharField(max_length=500)
    num_entry = serializers.IntegerField(min_value=0)

    def validate_admin_key(self, value):
        if value != os.environ.get('INDEXSWAPPER_ADMIN_KEY', '12345'):
            raise serializers.ValidationError('Invalid admin key!')
        return value

    def save(self):
        populate_modules(
            self.validated_data['num_entry'],
            self.validated_data['web_link'],
        )
        return {'message': 'Populated database successfully!'}


class CourseIndexPartialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseIndex
        fields = ('id', 'code', 'name', 'index', 'pending_count',)


class CourseIndexCompleteSerializer(serializers.ModelSerializer):
    datetime_added = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', read_only=True)
    information = serializers.CharField(write_only=True)
    information_data = serializers.SerializerMethodField(read_only=True)
    pending_dict = serializers.SerializerMethodField()

    class Meta:
        model = CourseIndex
        fields = ('id', 'code', 'name', 'index', 'datetime_added',
                  'information', 'information_data', 'pending_count', 'pending_dict',)
        read_only_fields = ('id', 'datetime_added',)

    def get_information_data(self, obj):
        try:
            return obj.get_information
        except IndexError or Exception:
            return []

    def get_pending_dict(self, obj):
        instances = SwapRequest.objects.filter(
            status=SwapRequest.Status.SEARCHING,
            current_index__code=obj.code)
        pending_dict = defaultdict(int)
        for instance in instances:
            for index in instance.get_wanted_indexes:
                if index == obj.index:
                    pending_dict[instance.current_index.index] += 1
        return pending_dict


class SwapRequestCreateSerializer(serializers.ModelSerializer):
    current_index_num = serializers.CharField(max_length=5, write_only=True)
    wanted_indexes = serializers.ListField(
        child=serializers.CharField(max_length=5),
        validators=[MinLengthValidator(1)])

    class Meta:
        model = SwapRequest
        fields = ('contact_info', 'contact_type',
                  'current_index_num', 'wanted_indexes')

    def create(self, validated_data):
        validated_data['current_index'] = CourseIndex.objects.get(
            index=validated_data['current_index_num'])
        del validated_data['current_index_num']
        for index in validated_data['wanted_indexes']:
            @lock_db_table(CourseIndex, CourseIndex.objects.get(index=index).id)
            def increment_pending_count(*args, **kwargs):
                course_index = kwargs['qs'].first()
                course_index.pending_count += 1
                course_index.save()
            increment_pending_count()
        return super().create(validated_data)

    def validate(self, data):
        user_sr_count = SwapRequest.objects.filter(user=self.context['request'].user).count()
        if user_sr_count >= MAX_SWAPREQUESTS_PER_USER:
            raise serializers.ValidationError(
                f'Bad request, user has reached maximum number of swap requests ({MAX_SWAPREQUESTS_PER_USER})')
        instance = get_object_or_404(
            CourseIndex,
            index=data['current_index_num'])
        if SwapRequest.objects.filter(
            user=self.context['request'].user,
            current_index=instance,
            status__in=[SwapRequest.Status.SEARCHING,
                        SwapRequest.Status.WAITING]
        ).count() != 0:
            raise ConflictValidationError(
                f'Conflict error, user already has a swap request for index {instance.index}')
        for index in data['wanted_indexes']:
            try:
                curr_courseindex = CourseIndex.objects.get(index=index)
            except CourseIndex.DoesNotExist:
                raise serializers.ValidationError(
                    f'Bad request, wanted index {index} does not exist')
            if curr_courseindex.index == instance.index:
                raise serializers.ValidationError(
                    f'Bad request, wanted index {index} cannot be the same as current index')
            if curr_courseindex.code != instance.code:
                raise serializers.ValidationError(
                    f'Bad request, wanted index {index} ({curr_courseindex.code}) should be the same course code with current index {index} ({instance.code})')
        return data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['course_code'] = instance.current_index.code
        data['course_name'] = instance.current_index.name
        data['current_index'] = instance.current_index.index
        data['id'] = instance.id
        return data


class SwapRequestListSerializer(serializers.ModelSerializer):
    datetime_added = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    datetime_found = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    wanted_indexes = serializers.SerializerMethodField()
    current_index = serializers.SerializerMethodField()
    course_code = serializers.SerializerMethodField()
    pair_contact_info = serializers.SerializerMethodField()
    pair_contact_type = serializers.SerializerMethodField()

    class Meta:
        model = SwapRequest
        fields = '__all__'

    def get_wanted_indexes(self, obj):
        try:
            return eval(obj.wanted_indexes)
        except:
            return obj.wanted_indexes

    def get_current_index(self, obj):
        return obj.current_index.index

    def get_course_code(self, obj):
        return obj.current_index.code

    def get_pair_contact_info(self, obj):
        if obj.pair:
            return obj.pair.contact_info
        return None

    def get_pair_contact_type(self, obj):
        if obj.pair:
            return obj.pair.contact_type
        return None


class SwapRequestEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = SwapRequest
        fields = ('contact_info', 'contact_type',)
