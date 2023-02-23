from django_filters import FilterSet
from event.models import MatricCheckIn

class MatricCheckInFilter(FilterSet):
    class Meta:
        model = MatricCheckIn
        fields = {
            'officer_name': ["exact"],
            'added_date': ["range"],
        }