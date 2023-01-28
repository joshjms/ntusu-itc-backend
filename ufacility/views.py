from rest_framework.views import APIView
from rest_framework.response import Response
from ufacility.models import Verification, Booking2, Venue, UFacilityUser
from ufacility.serializers import VerificationSerializer, BookingSerializer, VenueSerializer, UFacilityUserSerializer
from rest_framework import status
from ufacility.utils import send_email_to_security, send_booking_email_to_admins, send_verification_email_to_admins, clash_exists


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


# GET /users/<user_id>
class UserDetailView(APIView):
    def get(self, request, user_id):
        requesting_user = request.user
        requesting_ufacilityuser = UFacilityUser.objects.filter(user=requesting_user).first()

        # Check if requesting_user has a ufacility account
        if requesting_ufacilityuser == None:
            return Response({"message": "User does not have a UFacility account."}, status = status.HTTP_401_UNAUTHORIZED)

        ufacilityuser = UFacilityUser.objects.filter(id=user_id).first()

        # Only admins or the ufacility user itself can view the user details
        if requesting_ufacilityuser != ufacilityuser and requesting_ufacilityuser.is_admin == False:
            return Response({"message": "User is not a UFacility admin and not the user itself."}, status = status.HTTP_403_FORBIDDEN)

        # Check if ufacilityuser exists
        if ufacilityuser == None:
            return Response({"message": "User does not exist."}, status = status.HTTP_404_NOT_FOUND)

        serializer = UFacilityUserSerializer(ufacilityuser)
        return Response(serializer.data)


# GET /users/<user_id>/bookings
class UserBookingsView(APIView):
    def get(self, request, user_id):

        requesting_user = request.user
        requesting_ufacilityuser = UFacilityUser.objects.filter(user=requesting_user).first()

        # Check if requesting_user has a ufacility account
        if requesting_ufacilityuser == None:
            return Response({"message": "User does not have a UFacility account."}, status = status.HTTP_401_UNAUTHORIZED)

        ufacilityuser = UFacilityUser.objects.filter(id=user_id).first()

        # Only admins or the ufacility user itself can view the user bookings
        if requesting_ufacilityuser != ufacilityuser and requesting_ufacilityuser.is_admin == False:
            return Response({"message": "User is not a UFacility admin and not the user itself."}, status = status.HTTP_403_FORBIDDEN)

        # Check if ufacilityuser exists
        if ufacilityuser == None:
            return Response({"message": "UFacility user does not exist."}, status = status.HTTP_404_NOT_FOUND)

        bookings = Booking2.objects.filter(user=ufacilityuser)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)


# GET, POST /verifications
class VerificationView(APIView):
    def get(self, request):
        requesting_user = request.user
        requesting_ufacilityuser = UFacilityUser.objects.filter(user=requesting_user).first()

        # Check if requesting_user has a ufacility account
        if requesting_ufacilityuser == None:
            return Response({"message": "User does not have a UFacility account."}, status = status.HTTP_401_UNAUTHORIZED)

        # Only admins can view all verifications
        if requesting_ufacilityuser.is_admin == False:
            return Response({"message": "User is not a UFacility admin."}, status = status.HTTP_403_FORBIDDEN)

        verifications = Verification.objects.all()
        serializer = VerificationSerializer(verifications, many=True)
        return Response(serializer.data)

    def post(self, request):
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
        if serializer.is_valid():
            serializer.save()
            send_verification_email_to_admins()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


# GET, DELETE /verifications/<verification_id>
class VerificationDetailView(APIView):
    def get(self, request, verification_id):
        requesting_user = request.user
        requesting_ufacilityuser = UFacilityUser.objects.filter(user=requesting_user).first()
        verification = Verification.objects.filter(id=verification_id).first()

        # Check if requesting_user has a ufacility account
        if requesting_ufacilityuser == None:
            return Response({"message": "User does not have a UFacility account."}, status = status.HTTP_401_UNAUTHORIZED)

        # Only admins can view the verification details
        if requesting_ufacilityuser.is_admin == False:
            return Response({"message": "User is not a UFacility admin and not the owner of the verification."}, status = status.HTTP_403_FORBIDDEN)

        # Check if verification exists
        if verification == None:
            return Response({"message": "Verification does not exist."}, status = status.HTTP_404_NOT_FOUND)

        serializer = VerificationSerializer(verification)
        return Response(serializer.data)

    def delete(self, request, verification_id):
        requesting_user = request.user
        requesting_ufacilityuser = UFacilityUser.objects.filter(user=requesting_user).first()
        verification = Verification.objects.filter(id=verification_id).first()

        # Check if requesting_user has a ufacility account
        if requesting_ufacilityuser == None:
            return Response({"message": "User does not have a UFacility account."}, status = status.HTTP_401_UNAUTHORIZED)

        # Only admins can delete the verification
        if requesting_ufacilityuser.is_admin == False:
            return Response({"message": "User is not a UFacility admin."}, status = status.HTTP_403_FORBIDDEN)

        # Check if verification exists
        if verification == None:
            return Response({"message": "Verification does not exist."}, status = status.HTTP_404_NOT_FOUND)

        verification.delete()
        return Response({"message": "Verification deleted."}, status = status.HTTP_204_NO_CONTENT)

    def put(self, request, verification_id):
        requesting_user = request.user
        requesting_ufacilityuser = UFacilityUser.objects.filter(user=requesting_user).first()
        verification = Verification.objects.filter(id=verification_id).first()

        # Check if requesting_user has a ufacility account
        if requesting_ufacilityuser == None:
            return Response({"message": "User does not have a UFacility account."}, status = status.HTTP_401_UNAUTHORIZED)

        # Only admins can delete the verification
        if requesting_ufacilityuser.is_admin == False:
            return Response({"message": "User is not a UFacility admin."}, status = status.HTTP_403_FORBIDDEN)

        # Check if verification exists
        if verification == None:
            return Response({"message": "Verification does not exist."}, status = status.HTTP_404_NOT_FOUND)

        data = request.data
        data["user"] = verification.user.id
        serializer = VerificationSerializer(verification, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


# GET, POST /bookings
class BookingView(APIView):
    def get(self, request):
        bookings = Booking2.objects.all()
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request):
        requesting_user = request.user
        requesting_ufacilityuser = UFacilityUser.objects.filter(user=requesting_user).first()
        
        if requesting_ufacilityuser == None:
            return Response({"message": "User does not have a UFacility account."}, status = status.HTTP_401_UNAUTHORIZED)

        data = request.data
        data["user"] = requesting_ufacilityuser.id
        venue = Venue.objects.filter(name=data["venue"]).first()

        if venue == None:
            return Response({"message": "Venue does not exist."}, status = status.HTTP_400_BAD_REQUEST)

        data["venue"] = venue.id
        data["status"] = "pending"

        if clash_exists(venue.id, data["start_time"], data["end_time"]):
            return Response({"message": "Booking clashes with another booking."}, status = status.HTTP_409_CONFLICT)

        serializer = BookingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            send_booking_email_to_admins()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


# GET, PUT, DELETE /bookings/<booking_id>
class BookingDetailView(APIView):
    def get(self, request, booking_id):
        requesting_user = request.user
        requesting_ufacilityuser = UFacilityUser.objects.filter(user=requesting_user).first()
        booking = Booking2.objects.filter(id=booking_id).first()

        # Check if requesting_user has a ufacility account
        if requesting_ufacilityuser == None:
            return Response({"message": "User does not have a UFacility account."}, status = status.HTTP_401_UNAUTHORIZED)

        # Check if booking exists
        if booking == None:
            return Response({"message": "Booking does not exist."}, status = status.HTTP_404_NOT_FOUND)

        # Viewing specific bookings is only allowed for admins and the user who created the booking
        if requesting_ufacilityuser.is_admin == False and requesting_ufacilityuser != booking.user:
            return Response({"message": "User is not a UFacility admin and not the owner of the booking."}, status = status.HTTP_403_FORBIDDEN)

        serializer = BookingSerializer(booking)
        return Response(serializer.data)

    def put(self, request, booking_id):
        requesting_user = request.user
        requesting_ufacilityuser = UFacilityUser.objects.filter(user=requesting_user).first()
        booking = Booking2.objects.filter(id=booking_id).first()

        # Check if requesting_user has a ufacility account
        if requesting_ufacilityuser == None:
            return Response({"message": "User does not have a UFacility account."}, status = status.HTTP_401_UNAUTHORIZED)

        # Check if booking exists
        if booking == None:
            return Response({"message": "Booking does not exist."}, status = status.HTTP_404_NOT_FOUND)

        # Updating bookings is only allowed for admins and the user who created the booking
        if requesting_ufacilityuser.is_admin == False and requesting_ufacilityuser != booking.user:
            return Response({"message": "User is not a UFacility admin and not the owner of the booking."}, status = status.HTTP_403_FORBIDDEN)

        # Updating bookings is not allowed after it is accepted or declined
        if booking.status == "accepted" or booking.status == "declined":
            return Response({"message": "Booking is already accepted or declined. No further alteration is allowed."}, status = status.HTTP_409_CONFLICT)

        data = request.data
        venue = Venue.objects.filter(name=data["venue"]).first()

        if venue == None:
            return Response({"message": "Venue does not exist."}, status = status.HTTP_400_BAD_REQUEST)

        data["venue"] = venue.id
        data["user"] = requesting_ufacilityuser.id

        # Only admins can change status
        if requesting_ufacilityuser.is_admin == False or "status" not in data:
            data["status"] = booking.status

        serializer = BookingSerializer(booking, data=data, partial=True)
        if serializer.is_valid():
            # If the admin changes the status to "accepted", send an email to the security
            if requesting_ufacilityuser.is_admin and data["status"] == "accepted":
                send_email_to_security(venue, data["start_time"], data["end_time"])
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def delete(self, request, booking_id):
        requesting_user = request.user
        requesting_ufacilityuser = UFacilityUser.objects.filter(user=requesting_user).first()
        booking = Booking2.objects.filter(id=booking_id).first()

        # Check if requesting_user has a ufacility account
        if requesting_ufacilityuser == None:
            return Response({"message": "User does not have a UFacility account."}, status = status.HTTP_401_UNAUTHORIZED)

        # Check if booking exists
        if booking == None:
            return Response({"message": "Booking does not exist."}, status = status.HTTP_404_NOT_FOUND)

        # Delete is only allowed for admins and the user who created the booking
        if requesting_ufacilityuser.is_admin == False and requesting_ufacilityuser != booking.user:
            return Response({"message": "User is not a UFacility admin and not the owner of the booking."}, status = status.HTTP_403_FORBIDDEN)

        booking.delete()
        return Response({"message": "Booking deleted."}, status = status.HTTP_204_NO_CONTENT)


# GET, POST /venues
class VenueView(APIView):
    def get(self, request):
        venues = Venue.objects.all()
        serializer = VenueSerializer(venues, many=True)
        return Response(serializer.data)

    def post(self, request):
        requesting_user = request.user
        requesting_ufacilityuser = UFacilityUser.objects.filter(user=requesting_user).first()

        # Check if requesting_user has a ufacility account
        if requesting_ufacilityuser == None:
            return Response({"message": "User does not have a UFacility account."}, status = status.HTTP_401_UNAUTHORIZED)

        # POST is only allowed for admins
        if requesting_ufacilityuser.is_admin == False:
            return Response({"message": "User is not a UFacility admin."}, status = status.HTTP_403_FORBIDDEN)

        data = request.data
        serializer = VenueSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

