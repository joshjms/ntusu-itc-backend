from django.db.models import Value
from django.db.models.functions import Concat
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import BaseFilterBackend, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from modsoptimizer.models import CourseCode, CourseProgram


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


class CustomProgramSearch(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        program_qp = request.query_params.get('program__icontains', None)
        if not program_qp:
            return queryset
        programs_list = program_qp.split(';') if program_qp else None
        programs_list = [int(id.strip()) for id in programs_list if id.strip()]
        queryset = queryset.filter(programs__in=programs_list).distinct()
        return queryset


class CustomYearSearch(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        year_qp = request.query_params.get('year', None)
        if not year_qp or year_qp not in ['1', '2', '3', '4', '5']:
            return queryset
        year_qp = int(year_qp)
        course_programs = CourseProgram.objects.filter(year=year_qp).values_list('id', flat=True)
        queryset = queryset.filter(programs__in=course_programs).distinct()
        return queryset


class CourseCodeQueryParamsMixin:
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
        CustomCodeAndNameSearch,
        CustomCodeAndNameSearch2,
        CustomProgramSearch,
        CustomYearSearch,
    ]
    filterset_fields = {
        'code': ['icontains'],
        'name': ['icontains'],
        'academic_units': ['lte', 'gte'],
        'prerequisite': ['icontains'],
        'mutually_exclusive': ['icontains'],
        'not_available': ['icontains'],
        'not_available_all': ['icontains'],
        'offered_as_ue': ['exact'],
        'offered_as_bde': ['exact'],
        'grade_type': ['icontains'],
        'not_offered_as_core_to': ['icontains'],
        'not_offered_as_pe_to': ['icontains'],
        'not_offered_as_bde_ue_to': ['icontains'],
        'department_maintaining': ['icontains'],
        'program_list': ['icontains'],
    }
    ordering_fields = ['code', 'name', 'academic_units',]
    pagination_class = PaginationConfig


class CourseProgramQueryParamsMixin:
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        'name': ['icontains'],
        'year': ['exact'],
        'value': ['exact'],
    }
    ordering_fields = ['name', 'year', 'value',]
    pagination_class = PaginationConfig
