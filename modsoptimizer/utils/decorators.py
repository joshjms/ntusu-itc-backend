from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


def custom_swagger_index_schema(func):
    return swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter('start_index', openapi.IN_QUERY, description="Start index for scraping", type=openapi.TYPE_INTEGER, default=0),
            openapi.Parameter('end_index', openapi.IN_QUERY, description="End index for scraping", type=openapi.TYPE_INTEGER, default=None)
        ]
    )(func)
    
def swagger_course_code_list_schema(func):
    return swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('code__icontains', openapi.IN_QUERY, type=openapi.TYPE_STRING, default=None),
            openapi.Parameter('name__icontains', openapi.IN_QUERY, type=openapi.TYPE_STRING, default=None),
            openapi.Parameter('academic_units__lte', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, default=None),
            openapi.Parameter('academic_units__gte', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, default=None),
            openapi.Parameter('ordering', openapi.IN_QUERY, type=openapi.TYPE_STRING, default=None),
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, default=1),
            openapi.Parameter('page_size', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, default=10),
            
            openapi.Parameter('prerequisite__icontains', openapi.IN_QUERY, type=openapi.TYPE_STRING, default=None),
            openapi.Parameter('mutually_exclusive__icontains', openapi.IN_QUERY, type=openapi.TYPE_STRING, default=None),
            openapi.Parameter('not_available__icontains', openapi.IN_QUERY, type=openapi.TYPE_STRING, default=None),
            openapi.Parameter('not_available_all__icontains', openapi.IN_QUERY, type=openapi.TYPE_STRING, default=None),
            openapi.Parameter('offered_as_ue', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, default=None),
            openapi.Parameter('offered_as_bde', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, default=None),
            openapi.Parameter('grade_type__icontains', openapi.IN_QUERY, type=openapi.TYPE_STRING, default=None),
            openapi.Parameter('not_offered_as_core_to__icontains', openapi.IN_QUERY, type=openapi.TYPE_STRING, default=None),
            openapi.Parameter('not_offered_as_pe_to__icontains', openapi.IN_QUERY, type=openapi.TYPE_STRING, default=None),
            openapi.Parameter('not_offered_as_bde_ue_to__icontains', openapi.IN_QUERY, type=openapi.TYPE_STRING, default=None),
            openapi.Parameter('department_maintaining__icontains', openapi.IN_QUERY, type=openapi.TYPE_STRING, default=None),
            openapi.Parameter('program_list__icontains', openapi.IN_QUERY, type=openapi.TYPE_STRING, default=None),
            openapi.Parameter('program_code', openapi.IN_QUERY, type=openapi.TYPE_STRING, default=None),
            
            openapi.Parameter('search__icontains_2', openapi.IN_QUERY, type=openapi.TYPE_STRING, default=None),
            openapi.Parameter('program__icontains', openapi.IN_QUERY, type=openapi.TYPE_STRING, default=None),
            openapi.Parameter('year', openapi.IN_QUERY, type=openapi.TYPE_STRING, default=None),
            openapi.Parameter('level__in', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, default=None),
        ]
    )(func)
