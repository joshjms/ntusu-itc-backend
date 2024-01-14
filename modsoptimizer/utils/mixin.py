from django.db.models import Value
from django.db.models.functions import Concat
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import BaseFilterBackend, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from modsoptimizer.models import CourseCode, CourseIndex


class PaginationConfig(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'prev': self.get_previous_link(),
            'next': self.get_next_link(),
            'total_pages': self.page.paginator.num_pages,
            'results': data,
        })


class CustomCodeAndNameSearch(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        search_qp = request.query_params.get('search__icontains', None)
        if search_qp:
            search_qp = search_qp.replace('+', ' ')
            queryset = queryset.annotate(course_code_and_name=Concat('code', Value(' '), 'name'))
            return queryset.filter(course_code_and_name__icontains=search_qp)
        return queryset


class CustomCodeAndNameSearch2(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        search_qp = request.query_params.get('search__icontains_2', None)
        if search_qp:
            ret_queryset = CourseCode.objects.none()
            for search_term in search_qp.split():
                ret_queryset |= queryset.filter(
                    code__icontains=search_term) | queryset.filter(name__icontains=search_term)
            return ret_queryset
        else:
            return queryset


class CourseCodeQueryParamsMixin:
    filter_backends = [DjangoFilterBackend,
                       OrderingFilter,
                       CustomCodeAndNameSearch,
                       CustomCodeAndNameSearch2,]
    filterset_fields = {
        'code': ['icontains'],
        'name': ['icontains'],
        'academic_units': ['lte', 'gte'],
    }
    ordering_fields = ['code', 'name', 'academic_units',]
    pagination_class = PaginationConfig
