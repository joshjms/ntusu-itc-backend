from drf_yasg.utils import swagger_auto_schema
from django.http import Http404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ViewSet
from indexswapper.models import CourseIndex, SwapRequest
from indexswapper.serializers import (
    PopulateDatabaseSerializer,
    CourseIndexPartialSerializer,
    CourseIndexCompleteSerializer,
    SwapRequestCreateSerializer,
    SwapRequestListSerializer,
    SwapRequestEditSerializer,
)
from indexswapper.utils import email
from indexswapper.utils.algo import perform_pairing
from indexswapper.utils.decorator import get_swap_request_with_id_verify, verify_cooldown
from indexswapper.utils.description import API_DESCRIPTIONS, courseindex_search_qp, swaprequest_qp
from indexswapper.utils.mixin import (
    CourseIndexQueryParamsMixin,
    SwapRequestQueryParamsMixin,
)
from portal.permissions import IsSuperUser


class PopulateDatabaseView(CreateAPIView):
    queryset = CourseIndex.objects.all()
    serializer_class = PopulateDatabaseSerializer
    permission_classes = [IsSuperUser]


class CourseIndexViewSet(CourseIndexQueryParamsMixin,
                         ReadOnlyModelViewSet):
    queryset = CourseIndex.objects.all()
    lookup_field = 'index'

    def get_serializer_class(self):
        return (
            CourseIndexPartialSerializer if self.action == 'list'
            else CourseIndexCompleteSerializer
        )

    @swagger_auto_schema(operation_description=API_DESCRIPTIONS['courseindex_list'])
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)

    @swagger_auto_schema(operation_description=API_DESCRIPTIONS['courseindex_retrieve'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_description=API_DESCRIPTIONS['courseindex_get_courses'],
                         manual_parameters=[courseindex_search_qp])
    @action(methods=['get'], detail=False)
    def get_courses(self, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        unique_courses = qs.values('code', 'name').distinct()
        page = self.paginate_queryset(unique_courses)
        return self.get_paginated_response(page)

    @swagger_auto_schema(operation_description=API_DESCRIPTIONS['courseindex_get_indexes'])
    @action(methods=['get'], detail=False,
            url_path='get_indexes/(?P<course_code>[^/.]+)')
    def get_indexes_from_course(self, *args, **kwargs):
        qs = CourseIndex.objects.filter(code=kwargs['course_code'])
        if qs.count() == 0:
            raise Http404()
        return Response([{
            'index': x.index,
            'information': x.get_information,
            'pending_count': x.pending_count,
        } for x in qs])


class SwapRequestViewSet(SwapRequestQueryParamsMixin,
                         ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=SwapRequestCreateSerializer,
        operation_description=API_DESCRIPTIONS['swaprequest_create'])
    def create(self, request):
        serializer = SwapRequestCreateSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(user=request.user)
        email.send_swap_request_creation(instance)
        pair_result = perform_pairing(serializer.data['id'])
        return Response({**serializer.data, 'is_pair_success': pair_result},
                        status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        manual_parameters=[swaprequest_qp],
        operation_description=API_DESCRIPTIONS['swaprequest_list'])
    def list(self, request):
        queryset = SwapRequest.objects.filter(user=request.user.id)
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        serializer = SwapRequestListSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=SwapRequestEditSerializer,
        operation_description=API_DESCRIPTIONS['swaprequest_update'])
    @get_swap_request_with_id_verify(SwapRequest.Status.SEARCHING, SwapRequest.Status.WAITING)
    def update(self, request, *args, **kwargs):
        serializer = SwapRequestEditSerializer(
            instance=kwargs['instance'], data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data)

    @swagger_auto_schema(operation_description=API_DESCRIPTIONS['swaprequest_search_another'])
    @action(methods=['patch'], detail=True)
    @get_swap_request_with_id_verify(SwapRequest.Status.WAITING)
    @verify_cooldown()
    def search_another(self, request, *args, **kwargs):
        pair_result = perform_pairing(kwargs['instance'].id)
        pair_swaprequest = kwargs['instance'].pair
        pair_swaprequest.status = SwapRequest.Status.REVOKED
        pair_swaprequest.save()
        email.send_swap_search_another(kwargs['instance'])
        return Response({'is_pair_success': pair_result})

    @swagger_auto_schema(operation_description=API_DESCRIPTIONS['swaprequest_mark_complete'])
    @action(methods=['patch'], detail=True)
    @get_swap_request_with_id_verify(SwapRequest.Status.WAITING)
    def mark_complete(self, request, *args, **kwargs):
        kwargs['instance'].status = SwapRequest.Status.COMPLETED
        kwargs['instance'].save()
        kwargs['instance'].pair.status = SwapRequest.Status.COMPLETED
        kwargs['instance'].pair.save()
        email.send_swap_completed(kwargs['instance'])
        return Response('ok')

    @swagger_auto_schema(operation_description=API_DESCRIPTIONS['swaprequest_cancel_swap'])
    @action(methods=['patch'], detail=True)
    @get_swap_request_with_id_verify(SwapRequest.Status.WAITING, SwapRequest.Status.SEARCHING)
    def cancel_swap(self, request, *args, **kwargs):
        current_status = kwargs['instance'].status
        kwargs['instance'].status = SwapRequest.Status.REVOKED
        kwargs['instance'].save()
        if current_status == SwapRequest.Status.WAITING:
            perform_pairing(kwargs['instance'].pair.id)
            email.send_swap_cancel_pair(kwargs['instance'].pair)
        email.send_swap_cancel_self(
            kwargs['instance'], current_status == SwapRequest.Status.WAITING)
        return Response('ok')
