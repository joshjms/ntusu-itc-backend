from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from ufacility.models import Verification, Booking2, Venue, UFacilityUser
from ufacility.serializers import VerificationSerializer, BookingSerializer, VenueSerializer, UFacilityUserSerializer
from ufacility.utils import send_email_to_security, send_booking_email_to_admins, send_verification_email_to_admins, clash_exists
from ufacility import decorators


# POST /users
class UserView(APIView):
    @method_decorator(decorators.ufacility_admin_required)
    def post(self, request, **kwargs):
        serializer = UFacilityUserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)


# GET /users/<user_id>
class UserDetailView(APIView):
    @method_decorator(decorators.ufacilityuser_decorator)
    def get(self, request, user_id, **kwargs):
        ufacilityuser = get_object_or_404(UFacilityUser, id=user_id)
        serializer = UFacilityUserSerializer(ufacilityuser)
        return Response(serializer.data)
    
    # TODO (?) PUT: allow user (self) to only edit 'hongen_name' and 'hongen_phone_number'

    # TODO (?) DELETE: for admin to revoke access; delete ufacility user, change verification to rejected


# GET /users/<user_id>/bookings
class UserBookingsView(APIView):
    @method_decorator(decorators.ufacility_user_required)
    def get(self, request, user_id, **kwargs):
        requesting_ufacilityuser = kwargs['ufacilityuser']
        ufacilityuser = get_object_or_404(UFacilityUser, id=user_id)

        # Only admins or the ufacility user itself can view the user bookings
        if requesting_ufacilityuser != ufacilityuser and requesting_ufacilityuser.is_admin == False:
            return Response({"message": "User is not a UFacility admin and not the user itself."}, status = status.HTTP_403_FORBIDDEN)

        bookings = Booking2.objects.filter(user=ufacilityuser)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)


# GET, POST /verifications
class VerificationView(APIView):
    @method_decorator(decorators.ufacility_admin_required)
    def get(self, request, **kwargs):
        verifications = Verification.objects.all()
        serializer = VerificationSerializer(verifications, many=True)
        return Response(serializer.data)

    @method_decorator(decorators.login_required)
    def post(self, request, **kwargs):
        requesting_user = request.user
        requesting_ufacilityuser = UFacilityUser.objects.filter(user=requesting_user).first()
        verification = Verification.objects.filter(user=requesting_user).first()

        # Check if requesting_user already has a verification or a ufacility account
        if verification != None or requesting_ufacilityuser != None:
            return Response({"message": "User already has a verification or a UFacility account."}, status = status.HTTP_409_CONFLICT)

        data = request.data
        data["user"] = requesting_user.id
        data["status"] = "pending"
        serializer = VerificationSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            send_verification_email_to_admins()
            return Response(serializer.data, status = status.HTTP_201_CREATED)


# GET, DELETE /verifications/<verification_id>
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
    def put(self, request, verification_id, **kwargs): # TODO - evaluate the need of this endpoint
        verification = get_object_or_404(Verification, id=verification_id)
        data = request.data
        data["user"] = verification.user.id
        serializer = VerificationSerializer(verification, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)


# GET, POST /bookings
class BookingView(APIView):
    @method_decorator(decorators.login_required)
    def get(self, request, **kwargs):
        bookings = Booking2.objects.all()
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    @method_decorator(decorators.ufacility_user_required)
    def post(self, request, **kwargs):
        requesting_ufacilityuser = kwargs['ufacilityuser']

        data = request.data
        data["user"] = requesting_ufacilityuser.id
        venue = Venue.objects.filter(name=data["venue"]).first()

        if venue == None: # TODO - giving the id is fine!
            return Response({"message": "Venue does not exist."}, status = status.HTTP_400_BAD_REQUEST)

        data["venue"] = venue.id

        # TODO - put this to 'validate' method in serializer
        if clash_exists(venue.id, data["start_time"], data["end_time"]):
            return Response({"message": "Booking clashes with another booking."}, status = status.HTTP_409_CONFLICT)

        serializer = BookingSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            send_booking_email_to_admins()
            return Response(serializer.data, status = status.HTTP_201_CREATED)


# GET, PUT, DELETE /bookings/<booking_id>
class BookingDetailView(APIView):
    @method_decorator(decorators.ufacility_admin_or_booking_owner_required)
    def get(self, request, booking_id, **kwargs):
        serializer = BookingSerializer(kwargs["booking"])
        return Response(serializer.data)

    @method_decorator(decorators.ufacility_admin_or_booking_owner_required + decorators.pending_booking_only)
    def put(self, request, booking_id, **kwargs):
        booking = kwargs["booking"]
        requesting_ufacilityuser = kwargs["ufacilityuser"]

        data = request.data
        venue = get_object_or_404(Venue, name=data["venue"])
        data["venue"] = venue.id
        data["user"] = requesting_ufacilityuser.id

        # Only admins can change status
        if requesting_ufacilityuser.is_admin == False or "status" not in data:
            data["status"] = booking.status

        serializer = BookingSerializer(booking, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    @method_decorator(decorators.ufacility_admin_or_booking_owner_required)
    def delete(self, request, booking_id, **kwargs):
        kwargs['booking'].delete()
        return Response({"message": "Booking deleted."}, status=status.HTTP_204_NO_CONTENT)


# PUT /bookings/<booking_id>/accept/
class AcceptBookingView(APIView):
    @method_decorator(decorators.ufacility_admin_required + decorators.pending_booking_only)
    def put(self, request, booking_id, **kwargs):
        booking = kwargs['booking']
        booking.status = 'accepted'
        booking.save()
        send_email_to_security(booking.venue, booking.start_time, booking.end_time)
        # TODO - send email to ufacilityuser that their booking has been accepted
        return Response('booking accepted', status=status.HTTP_200_OK)


# PUT /bookings/<booking_id>/reject/
class RejectBookingView(APIView):
    @method_decorator(decorators.ufacility_admin_required + decorators.pending_booking_only)
    def put(self, request, booking_id, **kwargs):
        booking = kwargs['booking']
        booking.status = 'rejected'
        booking.save()
        # TODO - send email to ufacilityuser that their booking has been rejected
        return Response('booking rejected', status=status.HTTP_200_OK)


# GET, POST /venues
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
