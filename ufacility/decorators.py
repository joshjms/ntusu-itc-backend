from rest_framework.serializers import BaseSerializer
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Model
from django.shortcuts import get_object_or_404
from datetime import datetime as dt
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
            return Response({'message': 'Anonymous User (not logged in)'},
                status=status.HTTP_401_UNAUTHORIZED)
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
            return Response({'message': 'User does not have a UFacility account.'},
                status=status.HTTP_401_UNAUTHORIZED)
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
            return Response({'message': 'User is not a UFacility admin.'},
                status=status.HTTP_403_FORBIDDEN)
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
            return Response({'message': 'User is not a UFacility admin nor the owner of this instance.'},
                status=status.HTTP_403_FORBIDDEN)
        return func(request, *args, **kwargs)
    return wrapper


'''
    Return 409 if booking has been accepted or rejected.
'''
def _pending_booking_only(func: callable):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        booking = (kwargs['booking'] if 'booking' in kwargs else
            get_object_or_404(Booking2, id=kwargs['booking_id']))
        if booking.status in ['accepted', 'rejected']:
            return Response('Booking is already accepted or declined. No further alteration is allowed.',
                status=status.HTTP_409_CONFLICT)
        return func(request, *args, **kwargs)
    return wrapper


'''
    Return 409 if user already created a verification or already has ufacility account.
    Assumes that '_login_required' decorator has been applied.
'''
def _no_verification_and_ufacility_account(func: callable):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        requesting_ufacilityuser = UFacilityUser.objects.filter(user=request.user).first()
        verification = Verification.objects.filter(user=request.user).first()
        if verification != None or requesting_ufacilityuser != None:
            return Response({"message": "User already has a verification or a UFacility account."},
                status = status.HTTP_409_CONFLICT)
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


'''
    Accepts a booking queryset.
    Added filter, sort, pagination feature, based on query parameter.
    Store final bookings queryset in kwargs['booking'].
    Store pagination related info in kwargs['pagination_info'].

    Example:
    '?start_date=2023-01-19&end_date=2023-01-22&facility=1-3-4&status=pending-declined
    &sort=ascstart_time-desvenue__name-desid&items_per_page=3&page=2', means:
    Filter from date 19 Jan 2023 to 22 Jan 2023 inclusive, facility id 1 or 3 or 4,
    status pending or declined, sort by start time ascendingly, if there are ties
    sort by facility name descendingly, if there are ties sort by id descendingly,
    paginate 3 bookings per page, open page 2.
'''
def _booking_utilities(own_booking: bool=False):
    def decorator(func: callable):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if own_booking:
                bookings = Booking2.objects.filter(user=kwargs['ufacilityuser'])
            else:
                bookings = Booking2.objects.all()

            # filter feature
            filter_start_date = request.GET.get('start_date', '')
            filter_end_date = request.GET.get('end_date', '')
            filter_facility = request.GET.get('facility', '')
            filter_status = request.GET.get('status', '')
            filter_kwargs = {}
            try: filter_kwargs['date__gte'] = dt.strptime(filter_start_date, '%Y-%m-%d').date()
            except: pass
            try: filter_kwargs['date__lte'] = dt.strptime(filter_end_date, '%Y-%m-%d').date()
            except: pass
            if filter_facility: filter_kwargs['venue__id__in'] = filter_facility.split('-')
            if filter_status: filter_kwargs['status__in'] = filter_status.split('-')
            try: bookings = Booking2.objects.filter(**filter_kwargs)
            except: pass

            # sort feature
            sortcodes = request.GET.get('sort', 'ascid').split('-')
            try: bookings = bookings.order_by(*[('-' if sortcode[0:3] == 'des' else '') + \
                sortcode[3::] for sortcode in sortcodes])
            except: pass

            # dynamic pagination feature
            pagination_items_per_page = request.GET.get('items_per_page', 10)
            pagination_page = request.GET.get('page', 1)
            paginator = Paginator(bookings, pagination_items_per_page)
            try: paginator = Paginator(bookings, pagination_items_per_page)
            except: paginator = Paginator(bookings, 10)
            try: page = paginator.page(pagination_page)
            except PageNotAnInteger: page = paginator.page(1)
            except EmptyPage: page = paginator.page(paginator.num_pages)

            # store important data in kwargs
            kwargs['bookings'] = list(page)
            kwargs['pagination_info'] = {
                'has_next': page.has_next(), 'has_prev': page.has_previous(),
                'total_pages': paginator.num_pages
            }
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
pending_booking_only = [_pending_booking_only]
no_verification_and_ufacility_account = login_required + [_no_verification_and_ufacility_account]
booking_utilities = [_booking_utilities()]
booking_utilities_self = [_booking_utilities(True)]
