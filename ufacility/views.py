from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.forms.models import model_to_dict
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from ufacility.models import Verification, Venue, UFacilityUser, Booking2
from ufacility.serializers import (
    VerificationSerializer,
    BookingSerializer,
    BookingReadSerializer,
    VenueSerializer,
    UFacilityUserSerializer,
    BookingPartialSerializer
)
from ufacility import decorators, utils
from django.db.models import Q


# GET /check_user_status
class CheckStatusView(APIView):
    def get(self, request):
        requesting_user = request.user
        requesting_ufacilityuser = UFacilityUser.objects.filter(user=requesting_user).first()

        # Check if requesting_user is Anonymous User
        if requesting_user.is_anonymous:
            return Response({"message": "User is Anonymous.", "type": "anonymous"}, status = status.HTTP_401_UNAUTHORIZED)

        # Check if requesting_user has a ufacility account
        if requesting_ufacilityuser == None:
            return Response({"message": "User does not have a UFacility account.", "type": "sso user"}, status = status.HTTP_401_UNAUTHORIZED)

        # Check if requesting_user is a ufacility user
        if requesting_ufacilityuser.is_admin == False:
            return Response({"message": "User is a UFacility user.", "type": "ufacility user"}, status = status.HTTP_200_OK)

        # Otherwise, user is admin
        return Response({"message": "User is a UFacility admin.", "type": "ufacility admin"}, status = status.HTTP_200_OK)


# POST /users
class UserView(APIView):
    def post(self, request):
        requesting_user = request.user
        requesting_ufacilityuser = UFacilityUser.objects.filter(user=requesting_user).first()

        # Check if requesting_user has a ufacility account
        if requesting_ufacilityuser == None:
            return Response({"message": "User does not have a UFacility account."}, status = status.HTTP_401_UNAUTHORIZED)
        
        # Only admins can create ufacility users
        if requesting_ufacilityuser.is_admin == False:
            return Response({"message": "User is not a UFacility admin."}, status = status.HTTP_403_FORBIDDEN)

        data = request.data
        serializer = UFacilityUserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


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
    @method_decorator(decorators.ufacility_user_required + decorators.booking_utilities_self)
    def get(self, request, **kwargs):
        serializer = BookingReadSerializer(kwargs['bookings'], many=True)
        return Response({
            'bookings': serializer.data,
            'pagination_info': kwargs['pagination_info']
        })


# GET, POST /verifications/
class VerificationView(APIView):
    @method_decorator(decorators.ufacility_admin_required)
    def get(self, request, **kwargs):
        verifications = Verification.objects.all()
        filter_status = request.GET.get('status', '')
        if filter_status: verifications = verifications.filter(status__in=filter_status.split('-'))
        serializer = VerificationSerializer(verifications, many=True)
        return Response(serializer.data)

    @method_decorator(decorators.no_verification_and_ufacility_account)
    def post(self, request, **kwargs):
        serializer = VerificationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
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
    @method_decorator(decorators.login_required + decorators.booking_utilities)
    def get(self, request, **kwargs):
        serializer = BookingReadSerializer(kwargs['bookings'], many=True)
        return Response({
            'bookings': serializer.data,
            'pagination_info': kwargs['pagination_info']
        })

    @method_decorator(decorators.ufacility_user_required)
    def post(self, request, **kwargs):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=kwargs['ufacilityuser'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)


# GET, PUT, DELETE /bookings/<booking_id>/
class BookingDetailView(APIView):
    @method_decorator(decorators.ufacility_admin_or_booking_owner_required)
    def get(self, request, booking_id, **kwargs):
        serializer = BookingReadSerializer(kwargs["booking"])
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
        utils.send_email_to_security(booking.venue, booking.start_time, booking.end_time)
        # TODO - send email to ufacilityuser that their booking has been accepted
        ufacilityuser = booking.user
        user = ufacilityuser.user
        utils.send_booking_results_email(user.email, booking.venue, booking.start_time, booking.end_time, booking.status)
        return Response({'message': 'Booking accepted.'}, status=status.HTTP_200_OK)


# PUT /bookings/<booking_id>/reject/
class BookingRejectView(APIView):
    @method_decorator(decorators.ufacility_admin_required + decorators.pending_booking_only)
    def put(self, request, booking_id, **kwargs):
        booking = kwargs['booking']
        booking.status = 'declined'
        booking.save()
        # TODO - send email to ufacilityuser that their booking has been rejected
        ufacilityuser = booking.user
        user = ufacilityuser.user
        utils.send_booking_results_email(user.email, booking.venue, booking.start_time, booking.end_time, booking.status)
        return Response({'message': 'Booking rejected.'}, status=status.HTTP_200_OK)


# GET /bookings/<int:venue_id>/<str:date>/
class BookingHourlyView(APIView):
    @method_decorator(decorators.login_required)
    def get(self, request, venue_id, date):
        venue = get_object_or_404(Venue, id=venue_id)
        bookings = Booking2.objects.filter(Q(venue=venue), Q(date__date=date), Q(status='pending') | Q(status='accepted'))
        serializer = BookingPartialSerializer(bookings, many=True)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    '''
        TODO

        Given a venue id and a date,
        return for each hour,
        if that venue in that particular date (YYYY-MM-DD),
        is booked / soft-chopped (someone created booking but not confirmed) / rejected,
        and who booked / soft-chopped if there are any
        (basically all bookings that are in that book that venue in this date and hour)
    '''


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
