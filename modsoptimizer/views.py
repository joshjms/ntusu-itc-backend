from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from modsoptimizer.models import CourseCode, CourseIndex, CourseProgram
from modsoptimizer.serializers import (
    CourseCodePartialSerializer,
    CourseCodeSerializer,
    CourseIndexSerializer,
    CourseProgramSerializer,
    OptimizerInputSerialzer,
)
from modsoptimizer.utils.algo import optimize_index
from modsoptimizer.utils.course_additional_scraper import perform_course_additional
from modsoptimizer.utils.course_scraper import perform_course_scraping
from modsoptimizer.utils.decorators import custom_swagger_index_schema, swagger_course_code_list_schema
from modsoptimizer.utils.description_scraper import perform_description_scraping
from modsoptimizer.utils.exam_scraper import perform_exam_schedule_scraping
from modsoptimizer.utils.info_scraper import perform_info_update
from modsoptimizer.utils.mixin import CourseCodeQueryParamsMixin, CourseProgramQueryParamsMixin
from modsoptimizer.utils.program_scraper import perform_program_scraping
from portal.permissions import IsSuperUser


@api_view(['GET'])
@permission_classes([IsSuperUser])
def get_course_data(_):
    perform_course_scraping()
    return Response('Course Scraping Completed')


@api_view(['GET'])
@permission_classes([IsSuperUser])
def get_exam_data(_):
    perform_exam_schedule_scraping()
    return Response('Exam Scraping Completed')


@api_view(['GET'])
@permission_classes([IsSuperUser])
def get_info_data(_):
    perform_info_update()
    return Response('Info Update Completed')


@custom_swagger_index_schema
@api_view(['GET'])
@permission_classes([IsSuperUser])
def get_description_data(request):
    start_index = request.query_params.get('start_index', 0)
    end_index = request.query_params.get('end_index', CourseCode.objects.count())
    perform_description_scraping(int(start_index), int(end_index))
    return Response('Description Scraping Completed')


@custom_swagger_index_schema
@api_view(['GET'])
@permission_classes([IsSuperUser])
def get_program_data(request):
    start_index = request.query_params.get('start_index', 0)
    end_index = request.query_params.get('end_index')
    perform_program_scraping(int(start_index), int(end_index) if end_index else None)
    return Response('Program Scraping Completed')


@api_view(['GET'])
@permission_classes([IsSuperUser])
def get_course_additional_data(_):
    perform_course_additional()
    return Response('Course Additional Data Population Completed')


class CourseCodeListView(CourseCodeQueryParamsMixin, ListAPIView):
    serializer_class = CourseCodePartialSerializer
    queryset = CourseCode.objects.all()
    
    @swagger_course_code_list_schema
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CourseCodeDetailView(RetrieveAPIView):
    serializer_class = CourseCodeSerializer
    lookup_field = 'course_code'

    def get_object(self):
        return get_object_or_404(CourseCode, code=self.kwargs['course_code'])


class CourseIndexDetailView(RetrieveAPIView):
    serializer_class = CourseIndexSerializer
    lookup_field = 'course_index'

    def get_object(self):
        return get_object_or_404(CourseIndex, index=self.kwargs['course_index'])


class CourseProgramListView(CourseProgramQueryParamsMixin, ListAPIView):
    serializer_class = CourseProgramSerializer
    queryset = CourseProgram.objects.all()


class OptimizeView(CreateAPIView):
    serializer_class = OptimizerInputSerialzer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        output = optimize_index(serializer.validated_data)
        return Response(output)
