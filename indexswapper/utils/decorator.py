from datetime import timedelta
from functools import wraps
from django.db import transaction
from django.db.models import Model, QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone as tz
from rest_framework import status
from rest_framework.response import Response
from indexswapper.models import SwapRequest


def get_swap_request_with_id_verify(*allowed_status):
    '''
        Custom decorator that gets SwapRequest object by its id (given in url).
        Assumes that user is authenticated.
        Takes in allowed status args, which are the status allowed for the object.
        Return 404 if object is not found.
        Return 403 if requesting user is not owner of object.
        Return 400 if object status is not in allowed status.
        You can access the retrieved object from `kwargs['instance']`.
    '''
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            try:
                kwargs['pk'] = int(kwargs['pk'])
            except ValueError:
                return Response({
                    'error': f'ID received: {kwargs["pk"]} is not an integer!'
                }, status=status.HTTP_400_BAD_REQUEST)
            kwargs['instance'] = get_object_or_404(
                SwapRequest, id=kwargs['pk'])
            if kwargs['instance'].user != request.user:
                return Response({
                    'error': 'you are not the owner of this request'
                }, status=status.HTTP_403_FORBIDDEN)
            if kwargs['instance'].status not in allowed_status:
                return Response({
                    'error': f'only allow status of {allowed_status}'
                }, status=status.HTTP_400_BAD_REQUEST)
            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator


def verify_cooldown(COOLDOWN_HOURS=24):
    '''
        Custom decorator that verify SwapRequest object cooldown.
        It access the object from kwargs['instance'].
        Return 400 if object status is not in allowed COOLDOWN_HOURS has not passed.
        Else execute the main decorated function.
    '''
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            dt_found = kwargs['instance'].datetime_found
            if dt_found and tz.now() < dt_found + timedelta(hours=COOLDOWN_HOURS):
                return Response({
                    'error': 'waiting for cooldown',
                    'time_left': (dt_found + timedelta(hours=COOLDOWN_HOURS) - tz.now()) / 60
                }, status=status.HTTP_400_BAD_REQUEST)
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def lock_db_table(Entity: Model, id: int = 0):
    '''
        Decorator to wrap function under an atomic transaction and locks the database.
        If id is 0, it will lock the entire 'Entity' table.
        Otherwise, it will just lock the row with the given id of the 'Entity' table.
    '''
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with transaction.atomic():
                if id == 0:
                    qs = Entity.objects.all().select_for_update()
                else:
                    qs = Entity.objects.filter(
                        id=id).select_for_update()
                kwargs['qs']: QuerySet = qs
                return func(*args, **kwargs)
        return wrapper
    return decorator
