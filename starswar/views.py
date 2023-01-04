from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from starswar.models import CourseIndex, SwapRequest
from starswar.serializers import (
    CourseIndexPartialSerializer,
    CourseIndexCompleteSerializer,
)
from portal.permissions import IsSuperUser


class CourseIndexViewSet(ModelViewSet):
    queryset = CourseIndex.objects.all()
    lookup_field = 'index'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['code', 'index']

    def get_serializer_class(self):
        return (CourseIndexPartialSerializer if self.action == 'list'
            else CourseIndexCompleteSerializer)
    
    def get_permissions(self):
        self.permission_classes = ([] if self.request.method in
            ['GET', 'HEAD', 'OPTIONS'] else [IsSuperUser])
        return super().get_permissions()
    
    @action(methods=['get'], detail=False, url_name='get_courses',
        url_path='get_courses')
    def get_courses(self, *args, **kwargs):
        instances = CourseIndex.objects.all().distinct('code')
        return Response([{
            'code': x.code, 'name': x.name
        } for x in instances])
    
    @action(methods=['get'], detail=False, url_name='get_indexes',
        url_path='get_indexes/(?P<course_code>[^/.]+)')
    def get_indexes_from_course(self, *_, **kwargs):
        instances = CourseIndex.objects.filter(code=kwargs['course_code'])
        return Response([{
            'index': x.index, 'pending_count': x.pending_count,
            'information': x.get_information
        } for x in instances])

    # web scraper automatic data insertion TODO
    def populate_database(self):
        pass


class SwapRequestViewSet(ViewSet):
    pass
    # TODO
    # GET -> view all your swap request (filter search, wait, completed)
    # DELETE -> cancel swap, if pair is found auto search the pair
    # POST -> create request, mark as complete option or search again
