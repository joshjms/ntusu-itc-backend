from rest_framework.serializers import BaseSerializer
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Model
from django.shortcuts import get_object_or_404
from functools import wraps
from sso.models import User
from ufacility.models import UFacilityUser, Booking2, Verification
from ufacility.serializers import UFacilityUserSerializer, VerificationSerializer


'''
    Return 401 unauthorized with custom message if user is anonymous.
'''
def _login_required(func: callable):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_anonymous:
            return Response({'message': 'Anonymous User (not logged in)'}, status=status.HTTP_401_UNAUTHORIZED)
        return func(request, *args, **kwargs)
    return wrapper


'''
    Return 401 unauthorized with custom message if user is not a ufacility user.
    kwargs['ufacilityuser'] stores the ufacilityuser instance.
    Assumes that '_login_required' decorator has been applied.
'''
def _ufacility_user_required(func: callable):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        ufacilityuser = UFacilityUser.objects.filter(user=request.user).first()
        if ufacilityuser == None:
            return Response({'message': 'User does not have a UFacility account.'}, status=status.HTTP_401_UNAUTHORIZED)
        kwargs['ufacilityuser'] = ufacilityuser
        return func(request, *args, **kwargs)
    return wrapper


'''
    Return 403 forbidden if user is a ufacility user but not a ufacility admin.
    Assumes that '_ufacility_user_required' decorator has been applied.
'''
def _ufacility_admin_required(func: callable):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if kwargs['ufacilityuser'].is_admin == False:
            return Response({'message': 'User is not a UFacility admin.'}, status=status.HTTP_403_FORBIDDEN)
        return func(request, *args, **kwargs)
    return wrapper


'''
    Return 404 not found if booking_id is invalid.
    kwargs['booking'] stores the booking instance.
    Assumes that '_ufacility_user_required' decorator has been applied.
'''
def _ufacility_admin_or_booking_owner_required(func: callable):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        ufacilityuser = kwargs['ufacilityuser']
        kwargs['booking'] = get_object_or_404(Booking2, id=kwargs['booking_id'])
        if ufacilityuser.is_admin == False and ufacilityuser != kwargs['booking'].user:
            return Response({'message': 'User is not a UFacility admin nor the owner of this instance.'}, status=status.HTTP_403_FORBIDDEN)
        return func(request, *args, **kwargs)
    return wrapper


'''
    When the 'lookup' kwargs is 0, get that user's own instance in 'Model' using 'serializer'.
    Assumes that 'model' has one to one relationship with User.
    Assumes that 'login_required' decorator has been applied.
'''
def _get_own_instance_when_id_0(Model: Model, serializer: BaseSerializer, lookup: str='id'):
    def decorator(func: callable):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            id = kwargs[lookup]
            if id == 0:
                user = User.objects.get(id=request.user.id)
                instance = get_object_or_404(Model, user=user)
                sr = serializer(instance)
                return Response(sr.data)
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


login_required = [_login_required]
ufacility_user_required = login_required + [_ufacility_user_required]
ufacility_admin_required = ufacility_user_required + [_ufacility_admin_required]
ufacility_admin_or_booking_owner_required = ufacility_user_required + [_ufacility_admin_or_booking_owner_required]
ufacilityuser_decorator = login_required + [
    _get_own_instance_when_id_0(UFacilityUser, UFacilityUserSerializer, 'user_id'),
    _ufacility_user_required, _ufacility_admin_required]
verification_decorator = login_required + [
    _get_own_instance_when_id_0(Verification, VerificationSerializer, 'verification_id'),
    _ufacility_user_required, _ufacility_admin_required]
