from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ufacility.models import BookingGroup


def pending_booking_group_only(func):
    def wrapper(*args, **kwargs):
        booking_group = get_object_or_404(BookingGroup, id=kwargs['bookinggroup_id'])
        if booking_group.status != 'pending':
            return Response({'error': 'pending booking only'}, status=status.HTTP_409_CONFLICT)
        kwargs['booking_group'] = booking_group
        return func(*args, **kwargs)
    return wrapper
