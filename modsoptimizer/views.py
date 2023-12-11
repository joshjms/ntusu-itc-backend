from rest_framework.decorators import api_view
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from modsoptimizer.models import CourseCode
from modsoptimizer.serializers import (
    CourseCodePartialSerializer,
    CourseCodeSerializer,
    OptimizerInputSerialzer,
)
from modsoptimizer.utils.algo import optimize_index
from modsoptimizer.utils.course_scraper import perform_course_scraping
from modsoptimizer.utils.exam_scraper import perform_exam_schedule_scraping
from modsoptimizer.utils.mixin import CourseCodeQueryParamsMixin


@api_view(['GET'])
def get_course_data(_):
    perform_course_scraping()
    return Response('Course Scraping Completed')


@api_view(['GET'])
def get_exam_data(_):
    perform_exam_schedule_scraping()
    return Response('Exam Scraping Completed')


class CourseCodeListView(CourseCodeQueryParamsMixin, ListAPIView):
    serializer_class = CourseCodePartialSerializer
    queryset = CourseCode.objects.all()


class CourseCodeDetailView(RetrieveAPIView):
    serializer_class = CourseCodeSerializer
    lookup_field = 'course_code'

    def get_object(self):
        return CourseCode.objects.get(code=self.kwargs['course_code'])


class OptimizeView(CreateAPIView):
    serializer_class = OptimizerInputSerialzer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        output = optimize_index(serializer.validated_data)
        return Response(output)
