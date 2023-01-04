from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.decorators import action
from starswar.models import CourseIndex, SwapRequest
from starswar.serializers import (
    CourseIndexPartialSerializer,
    CourseIndexCompleteSerializer,
)
from portal.permissions import IsSuperUser


class CourseIndexViewSet(ModelViewSet):
    queryset = CourseIndex.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        return (CourseIndexPartialSerializer if self.action == 'list'
            else CourseIndexCompleteSerializer)
    
    def get_permissions(self):
        self.permission_classes = ([] if self.request.method in
            ['GET', 'HEAD', 'OPTIONS'] else [IsSuperUser])
        return super().get_permissions()
    
    # web scraper automatic data insertion TODO
    # settings configuration model TODO


class SwapRequestViewSet(ViewSet):
    pass
    # TODO
    # GET -> view all your swap request (filter search, wait, completed)
    # DELETE -> cancel swap, if pair is found auto search the pair
    # POST -> create request, mark as complete option or search again
