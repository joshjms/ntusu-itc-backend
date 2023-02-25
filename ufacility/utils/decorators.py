from rest_framework.response import Response
from rest_framework import status
from django.db.models import Model
from django.shortcuts import get_object_or_404
from functools import wraps
from ufacility.models import BookingGroup, UFacilityUser, Verification
from sso.models import User


def pending_booking_group_only(func: callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        booking_group = get_object_or_404(BookingGroup, id=kwargs['bookinggroup_id'])
        if booking_group.status != 'pending':
            return Response({'error': 'pending booking only'}, status=status.HTTP_409_CONFLICT)
        kwargs['booking_group'] = booking_group
        return func(*args, **kwargs)
    return wrapper


def no_verification_and_ufacility_account(func: callable):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        requesting_ufacilityuser = UFacilityUser.objects.filter(user=request.user).first()
        verification = Verification.objects.filter(user=request.user).first()
        if verification != None or requesting_ufacilityuser != None:
            return Response({"message": "User already has a verification or a UFacility account."},
                status = status.HTTP_409_CONFLICT)
        return func(request, *args, **kwargs)
    return wrapper


def get_own_instance_if_id_0(model: Model):
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            if kwargs[self.lookup_url_kwarg] == 0:
                user = User.objects.get(id=request.user.id)
                instance = get_object_or_404(model, user=user)
                sr = self.get_serializer_class()(instance)
                return Response(sr.data)
            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator
