from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.forms.models import model_to_dict
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from ufacility.models import Verification, Booking2, Venue, UFacilityUser
from ufacility.serializers import VerificationSerializer, BookingSerializer, VenueSerializer, UFacilityUserSerializer
from ufacility.utils import send_email_to_security, send_booking_email_to_admins, send_verification_email_to_admins
from ufacility import decorators
from datetime import datetime as dt


# GET /check_status/
class CheckStatusView(APIView):
    def get(self, request):
        pass
    '''
        TODO
        Given the current request, identify whether:
        - User is a ufacility admin OR
        - User is a ufacility user OR
        - User is a regular sso user OR
        - Anonymous user
    '''


# GET /users/<user_id>/
class UserDetailView(APIView):
    @method_decorator(decorators.ufacilityuser_decorator)
    def get(self, request, user_id, **kwargs):
        ufacilityuser = get_object_or_404(UFacilityUser, id=user_id)
        serializer = UFacilityUserSerializer(ufacilityuser)
        return Response(serializer.data)
    
    @method_decorator(decorators.ufacility_user_required)
    def put(self, request, user_id, **kwargs):
        ufacilityuser = kwargs['ufacilityuser']
        if ufacilityuser.user != request.user or not ufacilityuser.is_admin:
            return Response('You are not ufacility admin nor the owner of this instance',
                status=status.HTTP_403_FORBIDDEN)
        serializer = UFacilityUserSerializer(ufacilityuser, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)


# GET /users/<user_id>/bookings/
class UserBookingsView(APIView):
    @method_decorator(decorators.ufacility_user_required)
    def get(self, request, user_id, **kwargs):
        requesting_ufacilityuser = kwargs['ufacilityuser']
        ufacilityuser = get_object_or_404(UFacilityUser, id=user_id)

        # Only admins or the ufacility user itself can view the user bookings
        if requesting_ufacilityuser != ufacilityuser and requesting_ufacilityuser.is_admin == False:
            return Response({"message": "User is not a UFacility admin and not the user itself."}, status = status.HTTP_403_FORBIDDEN)
        # TODO - isn't this weird??? other endpoints are open for everyone, why not this one?
        # consider making partial and complete serializer for booking (?)

        bookings = Booking2.objects.filter(user=ufacilityuser)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)


# GET, POST /verifications/
class VerificationView(APIView):
    @method_decorator(decorators.ufacility_admin_required)
    def get(self, request, **kwargs):
        verifications = Verification.objects.all()
        serializer = VerificationSerializer(verifications, many=True)
        return Response(serializer.data)

    @method_decorator(decorators.no_verification_and_ufacility_account)
    def post(self, request, **kwargs):
        serializer = VerificationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            send_verification_email_to_admins()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


# GET, DELETE /verifications/<verification_id>/
class VerificationDetailView(APIView):
    @method_decorator(decorators.verification_decorator)
    def get(self, request, verification_id, **kwargs):
        verification = get_object_or_404(Verification, id=verification_id)
        serializer = VerificationSerializer(verification)
        return Response(serializer.data)

    @method_decorator(decorators.ufacility_admin_required)
    def delete(self, request, verification_id, **kwargs): # TODO - evaluate the need of this endpoint
        verification = get_object_or_404(Verification, id=verification_id)
        verification.delete()
        return Response({"message": "Verification deleted."}, status = status.HTTP_204_NO_CONTENT)

    @method_decorator(decorators.ufacility_admin_required)
    def put(self, request, verification_id, **kwargs): # TODO - evaluate the need of this endpoint, can edit even when rejected or accepted ???
        verification = get_object_or_404(Verification, id=verification_id)
        data = request.data
        data["user"] = verification.user.id
        serializer = VerificationSerializer(verification, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)


# PUT /verifications/<verification_id>/accept/
class VerificationAcceptView(APIView):
    @method_decorator(decorators.ufacility_admin_required)
    def put(self, request, verification_id, **kwargs):
        verification = get_object_or_404(Verification, id=verification_id)
        verification.status = 'accepted'
        verification.save()
        if UFacilityUser.objects.filter(user=verification.user).count() == 0:
            UFacilityUser.objects.create(
                user=verification.user,
                is_admin=False,
                **model_to_dict(verification, fields=['cca', 'hongen_name', 'hongen_phone_number'])
            )
            return Response({'message': 'Verification accepted.'})
        return Response({'message': 'Verication has been accepted and ufacility user model existed.'},
            status=status.HTTP_409_CONFLICT)


# PUT /verifications/<verification_id>/reject/
class VerificationRejectView(APIView):
    @method_decorator(decorators.ufacility_admin_required)
    def put(self, request, verification_id, **kwargs):
        verification = get_object_or_404(Verification, id=verification_id)
        if verification.status == 'declined':
            UFacilityUser.objects.filter(user=verification.user).delete() # just in case
            return Response({'message': 'Verification has been declined and no such ufacility user model.'},
                status=status.HTTP_409_CONFLICT)
        verification.status = 'declined'
        verification.save()
        deleted, _ = UFacilityUser.objects.filter(user=verification.user).delete()
        if deleted == 1:
            return Response({'message': 'Access revoked.'})
        return Response({'message': 'Verification rejected.'})


# GET, POST /bookings/
class BookingView(APIView):
    @method_decorator(decorators.login_required)
    def get(self, request, **kwargs):
        bookings = Booking2.objects.all()

        # TODO - create test cases, move this to or decorator, check logic!
        # just doing this real quick so frontend can work
        from django.db.models import Q # TODO - can filter multiple selection

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
        if filter_facility: filter_kwargs['venue__name'] = filter_facility
        bookings = Booking2.objects.filter(**filter_kwargs)
        if filter_status: filter_kwargs['status'] = filter_status

        # sort feature - TODO
        sortcodes = request.GET.get('sort', 'ascid').split('-')
        try: bookings.order_by(*[('-' if sortcode[0:3:] == 'des' else '') + \
            sortcode[3::] for sortcode in sortcodes])
        except: pass

        # dynamic pagination feature
        '''
        TODO - here are a bit of starter code (untested)
        Example usage: assume there are 25 bookings id 1 - 25
        By default, you get bookings id 1-10
        If ?page=2, get bookings id 11-20
        If ?page=3, get bookings id 21-25
        If ?page=999, get bookings id 21-25
        If ?page=abc, get bookings id 1-10
        If ?items_per_page=8&page=2, get bookings id 9-16
        Also return information of whether next & prev page num valid or not
        '''
        from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
        pagination_items_per_page = request.GET.get('items_per_page', 10)
        pagination_page = request.GET.get('page', 10)
        paginator = Paginator(bookings, pagination_items_per_page)
        try:
            paginator = Paginator(bookings, pagination_items_per_page)
        except:
            paginator = Paginator(bookings, 10)
        try:
            page = paginator.page(pagination_page)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)

        serializer = BookingSerializer(list(bookings), many=True)
        return Response({
            'bookings': serializer.data,
            'pagination_info': {
                'has_next': page.has_next(), 'has_prev': page.has_previous(),
            }
        })

    @method_decorator(decorators.ufacility_user_required)
    def post(self, request, **kwargs):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            send_booking_email_to_admins()
            return Response(serializer.data, status = status.HTTP_201_CREATED)


# GET, PUT, DELETE /bookings/<booking_id>/
class BookingDetailView(APIView):
    @method_decorator(decorators.ufacility_admin_or_booking_owner_required)
    def get(self, request, booking_id, **kwargs):
        serializer = BookingSerializer(kwargs["booking"])
        return Response(serializer.data)

    @method_decorator(decorators.ufacility_admin_or_booking_owner_required + decorators.pending_booking_only)
    def put(self, request, booking_id, **kwargs):
        serializer = BookingSerializer(kwargs["booking"], data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    @method_decorator(decorators.ufacility_admin_or_booking_owner_required)
    def delete(self, request, booking_id, **kwargs):
        kwargs['booking'].delete()
        return Response({"message": "Booking deleted."}, status=status.HTTP_204_NO_CONTENT)


# PUT /bookings/<booking_id>/accept/
class BookingAcceptView(APIView):
    @method_decorator(decorators.ufacility_admin_required + decorators.pending_booking_only)
    def put(self, request, booking_id, **kwargs):
        booking = kwargs['booking']
        booking.status = 'accepted'
        booking.save()
        send_email_to_security(booking.venue, booking.start_time, booking.end_time)
        # TODO - send email to ufacilityuser that their booking has been accepted
        return Response('Booking accepted.', status=status.HTTP_200_OK)


# PUT /bookings/<booking_id>/reject/
class BookingRejectView(APIView):
    @method_decorator(decorators.ufacility_admin_required + decorators.pending_booking_only)
    def put(self, request, booking_id, **kwargs):
        booking = kwargs['booking']
        booking.status = 'rejected'
        booking.save()
        # TODO - send email to ufacilityuser that their booking has been rejected
        return Response('Booking rejected.', status=status.HTTP_200_OK)


# GET, POST /venues/
class VenueView(APIView):
    @method_decorator(decorators.login_required)
    def get(self, request, **kwargs):
        venues = Venue.objects.all()
        serializer = VenueSerializer(venues, many=True)
        return Response(serializer.data)

    @method_decorator(decorators.ufacility_admin_required)
    def post(self, request, **kwargs):
        serializer = VenueSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


# PUT /venues/<venue_id>/
class VenueDetailView(APIView):
    @method_decorator(decorators.ufacility_admin_required)
    def put(self, request, venue_id, **kwargs):
        venue = get_object_or_404(Venue, id=venue_id)
        serializer = VenueSerializer(venue, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
