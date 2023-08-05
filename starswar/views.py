from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from starswar.models import XCourseIndex as CourseIndex, XSwapRequest as SwapRequest
from starswar.serializers import (
    XCourseIndexPartialSerializer as CourseIndexPartialSerializer,
    XCourseIndexCompleteSerializer as CourseIndexCompleteSerializer,
    XSwapRequestSerializer as SwapRequestSerializer,
)
from starswar.utils import util_algo, util_email, util_scraper
from starswar.utils.decorator import verify_cooldown, get_swap_request_with_id_verify
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
    
    @action(methods=['get'], detail=False)
    def get_courses(self, *args, **kwargs):
        instances = CourseIndex.objects.all().distinct('code')
        return Response([{
            'code': x.code, 'name': x.name
        } for x in instances])
    
    @action(methods=['get'], detail=False, url_name='get_indexes',
        url_path='get_indexes/(?P<course_code>[^/.]+)')
    def get_indexes_from_course(self, *args, **kwargs):
        instances = CourseIndex.objects.filter(code=kwargs['course_code'])
        return Response([{
            'index': x.index, 'pending_count': x.pending_count,
            'information': x.get_information
        } for x in instances])
    
    @action(methods=['post'], detail=False, serializer_class=None)
    def populate_database(self, *args, **kwargs):
        util_scraper.populate_modules()
        return Response('Process ongoing, it may take a few minutes!')


class SwapRequestViewSet(ViewSet):
    '''
        Create new swap request (need contact_info, current_index, wanted_indexes), by default has 'SEARCHING' status.
        Perform pairing algorithm for every swap request created.
        Email the user for confirmation that swap request has been created.
        If any pair is found, email both users that pair has been found.
    '''
    def create(self, request):
        serializer = SwapRequestSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user.id)
            util_email.send_swap_request_creation()
            util_algo.pairing_algorithm()
            return Response(serializer.data)

    '''
        Gets all of this user's swap request instances.
        If query parameter of status is given, filter based on status.
        For example, ?status=W for waiting status only.
        Valid query parameters are: ?status=W, ?status=S, ?status=C.
        For SuperUser, get all swap request instances created by all users.
    '''
    def list(self, request):
        filter_kw = {}
        if not request.user.is_superuser: filter_kw['user'] = request.user.id
        status = request.GET.get('status')
        if status: filter_kw['status'] = status
        qs = SwapRequest.objects.filter(**filter_kw)
        serializer = SwapRequestSerializer(qs, many=True)
        return Response(serializer.data)

    '''
        Applicable for swap request with status of 'WAITING', only allow user's own swap request and after some cooldown time.
        Change the user status to 'SEARCHING' and reinitiate pairing algorithm.
        Email the user for reinitiating search confirmation.
    '''
    @action(methods=['patch'], detail=True)
    @get_swap_request_with_id_verify(SwapRequest.Status.WAITING)
    @verify_cooldown()
    def search_another(self, *args, **kwargs):
        util_algo.pairing_algorithm()
        util_email.send_swap_search_another()
        return Response('ok')
    
    '''
        Applicable for swap request with status of 'WAITING', only allow user's own swap request.
        Change the user status to 'COMPLETED'.
        Email the user for completed swap confirmation.
    '''
    @action(methods=['patch'], detail=True)
    @get_swap_request_with_id_verify(SwapRequest.Status.WAITING)
    def mark_complete(self, *args, **kwargs):
        kwargs['sr'].status = SwapRequest.Status.COMPLETED
        kwargs['sr'].save()
        util_email.send_swap_completed()
        return Response('ok')
    
    '''
        Applicable for swap request with status of 'SEACHING' or 'WAITING', only allow user's own swap request.
        If status is 'SEARCHING', simply delete this swap request instance.
        If status is 'WAITING', delete this swap request instance, change pair's swap request instance status to 'WATING' and reinitiate pairing algorithm.
        Email the user for deletion confirmation, warn user not to do it again.
        If status is 'WAITING', email its pair that their pair has decided to cancel swap and they will be soon paired with another people.
    '''
    @action(methods=['patch'], detail=True)
    @get_swap_request_with_id_verify(SwapRequest.Status.WAITING, SwapRequest.Status.SEARCHING)
    def cancel(self, *args, **kwargs):
        if kwargs['sr'].status == SwapRequest.Status.COMPLETED:
            kwargs['sr'].delete()
        elif kwargs['sr'].status == SwapRequest.Status.WAITING:
            util_algo.pairing_algorithm()
            util_email.send_swap_cancel_pair()
        util_email.send_swap_cancel_self()
        return Response('ok')
