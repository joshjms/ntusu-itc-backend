from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from modsoptimizer.models import CourseCode, CourseIndex
from modsoptimizer.serializers import (
    CourseCodePartialSerializer,
    CourseCodeSerializer,
    CourseIndexSerializer,
    OptimizerInputSerialzer,
)
from modsoptimizer.utils.algo import optimize_index
from modsoptimizer.utils.course_scraper import perform_course_scraping
from modsoptimizer.utils.description_scraper import perform_description_scraping
from modsoptimizer.utils.exam_scraper import perform_exam_schedule_scraping
from modsoptimizer.utils.info_scraper import perform_info_update
from modsoptimizer.utils.mixin import CourseCodeQueryParamsMixin
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


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('start_index', openapi.IN_QUERY, description="Start index for scraping", type=openapi.TYPE_INTEGER, default=0),
        openapi.Parameter('end_index', openapi.IN_QUERY, description="End index for scraping", type=openapi.TYPE_INTEGER, default=None)
    ]
)
@api_view(['GET'])
@permission_classes([IsSuperUser])
def get_description_data(request):
    start_index = request.query_params.get('start_index', 0)
    end_index = request.query_params.get('end_index', CourseCode.objects.count())
    perform_description_scraping(int(start_index), int(end_index))
    return Response('Description Scraping Completed')


class CourseCodeListView(CourseCodeQueryParamsMixin, ListAPIView):
    serializer_class = CourseCodePartialSerializer
    queryset = CourseCode.objects.all()


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


class OptimizeView(CreateAPIView):
    serializer_class = OptimizerInputSerialzer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        output = optimize_index(serializer.validated_data)
        return Response(output)
