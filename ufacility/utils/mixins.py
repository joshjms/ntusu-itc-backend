from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from sso.models import User


class PaginationConfig(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'results': data,
        })


class BookingGroupUtilMixin:
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        'start_time': ['lt', 'gt'],
        'end_time': ['lt', 'gt'],
        'start_date': ['lt', 'gt'],
        'end_date': ['lt', 'gt'],
        'venue': ['exact'],
        'recurring': ['exact'],
    }
    ordering_fields = '__all__'
    pagination_class = PaginationConfig


class GetOwnInstanceMixin:
    own_instance_mixin_model = None

    def get(self, request, *args, **kwargs):
        assert self.own_instance_mixin_model is not None, ('Improperly Configured')
        if kwargs[self.lookup_url_kwarg] == 0:
            user = User.objects.get(id=request.user.id)
            instance = get_object_or_404(self.own_instance_mixin_model, user=user)
            sr = self.get_serializer_class()(instance)
            return Response(sr.data)
        return super().get(request, *args, **kwargs)
