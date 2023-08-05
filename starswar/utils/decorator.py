from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone as tz
from starswar.models import XSwapRequest as SwapRequest
from functools import wraps


'''
    Custom decorator that gets SwapRequest object by its id (given in url).
    Takes in allowed status args, which are the status allowed for the object.
    Return 404 if object is not found.
    Return 400 if object status is not in allowed status.
    You can access the retrieved object from kwargs['sr']
'''
def get_swap_request_with_id_verify(*allowed_status):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            kwargs['sr'] = get_object_or_404(SwapRequest, id=kwargs['id'])
            if kwargs['sr'].status not in allowed_status:
                return Response({
                    'error': f'only allow status of {allowed_status}'
                }, status=status.HTTP_400_BAD_REQUEST)
            return func(*args, **kwargs)
        return wrapper
    return decorator


'''
    Custom decorator that verify SwapRequest object cooldown.
    It access the object from kwargs['sr'].
    Return 400 if object status is not in allowed COOLDOWN_HOURS has not passed.
    Else execute the main decorated function.
'''
def verify_cooldown(COOLDOWN_HOURS=24):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            dt_found = kwargs['sr'].datetime_found
            if tz.now() < dt_found + COOLDOWN_HOURS:
                return Response({
                    'error': 'waiting for cooldown',
                    'time_left': -tz.now() + dt_found + COOLDOWN_HOURS
                }, status=status.HTTP_400_BAD_REQUEST)
            return func(*args, **kwargs)
        return wrapper
    return decorator
