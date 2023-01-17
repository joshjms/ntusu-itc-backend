from rest_framework.views import APIView
from rest_framework.response import Response
from ufacility.models import Verification, Booking, Venue, UFacilityUser
from ufacility.serializers import VerificationSerializer, BookingSerializer, VenueSerializer, UFacilityUserSerializer
from rest_framework import status
from sso.utils import send_email


exco_email = ""


# Clash check
def clash_exists(venue, day, start_time, end_time):
    bookings = Booking.objects.filter(venue=venue, date=day)
    for booking in bookings:
        if start_time < booking.end_time and end_time > booking.start_time:
            return True
    return False


# POST /users
class UserView(APIView):
    def post(self, request):
        requesting_user = request.user
        requesting_ufacilityuser = UFacilityUser.objects.filter(user=requesting_user).first()

        # Check if requesting_user has a ufacility account
        if requesting_ufacilityuser == None:
            return Response({"status": status.HTTP_401_UNAUTHORIZED, "message": "User does not have a UFacility account."})
        
        # Only admins can create ufacility users
        if requesting_ufacilityuser.is_admin == False:
            return Response({"status": status.HTTP_403_FORBIDDEN, "message": "User is not a UFacility admin."})

        data = request.data
        serializer = UFacilityUserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid data."})


# GET /users/<user_id>
class UserDetailView(APIView):
    def get(self, request, user_id):
        requesting_user = request.user
        requesting_ufacilityuser = UFacilityUser.objects.filter(user=requesting_user).first()

        # Check if requesting_user has a ufacility account
        if requesting_ufacilityuser == None:
            return Response({"status": status.HTTP_401_UNAUTHORIZED, "message": "User does not have a UFacility account."})

        ufacilityuser = UFacilityUser.objects.filter(id=user_id).first()

        # Only admins or the ufacility user itself can view the user details
        if requesting_ufacilityuser != ufacilityuser and requesting_ufacilityuser.is_admin == False:
            return Response({"status": status.HTTP_403_FORBIDDEN, "message": "User is neither a UFacility admin nor the user itself."})

        # Check if ufacilityuser exists
        if ufacilityuser == None:
            return Response({"status": status.HTTP_404_NOT_FOUND, "message": "UFacility user does not exist."})


        serializer = UFacilityUserSerializer(ufacilityuser)
        return Response(serializer.data)


# GET /users/<user_id>/bookings
class UserBookingsView(APIView):
    def get(self, request, user_id):

        requesting_user = request.user
        requesting_ufacilityuser = UFacilityUser.objects.filter(user=requesting_user).first()

        # Check if requesting_user has a ufacility account
        if requesting_ufacilityuser == None:
            return Response({"status": status.HTTP_401_UNAUTHORIZED, "message": "User does not have a UFacility account."})

        ufacilityuser = UFacilityUser.objects.filter(id=user_id).first()

        # Only admins or the ufacility user itself can view the user bookings
        if requesting_ufacilityuser != ufacilityuser and requesting_ufacilityuser.is_admin == False:
            return Response({"status": status.HTTP_403_FORBIDDEN, "message": "User is neither a UFacility admin nor the user itself."})

        # Check if ufacilityuser exists
        if ufacilityuser == None:
            return Response({"status": status.HTTP_404_NOT_FOUND, "message": "UFacility user does not exist."})

        bookings = Booking.objects.filter(user=ufacilityuser)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)


# GET, POST /verifications
class VerificationView(APIView):
    def get(self, request):
        requesting_user = request.user
        requesting_ufacilityuser = UFacilityUser.objects.filter(user=requesting_user).first()

        # Check if requesting_user has a ufacility account
        if requesting_ufacilityuser == None:
            return Response({"status": status.HTTP_401_UNAUTHORIZED, "message": "User does not have a UFacility account."})

        # Only admins can view all verifications
        if requesting_ufacilityuser.is_admin == False:
            return Response({"status": status.HTTP_403_FORBIDDEN, "message": "User is not a UFacility admin."})

        verifications = Verification.objects.all()
        serializer = VerificationSerializer(verifications, many=True)
        return Response(serializer.data)

    def post(self, request):
        requesting_user = request.user
        requesting_ufacilityuser = UFacilityUser.objects.filter(user=requesting_user).first()
        verification = Verification.objects.filter(user=requesting_user).first()

        # Check if requesting_user already has a verification or a ufacility account
        if verification != None or requesting_ufacilityuser != None:
            return Response({"status": status.HTTP_409_CONFLICT, "message": "User already has a verification or a UFacility account."})

        data = request.data
        data["user"] = requesting_user.id
        serializer = VerificationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid data."})


# GET, DELETE /verifications/<verification_id>
class VerificationDetailView(APIView):
    def get(self, request, verification_id):
        requesting_user = request.user
        requesting_ufacilityuser = UFacilityUser.objects.filter(user=requesting_user).first()
        verification = Verification.objects.filter(id=verification_id).first()

        # Check if requesting_user has a ufacility account
        if requesting_ufacilityuser == None:
            return Response({"status": status.HTTP_401_UNAUTHORIZED, "message": "User does not have a UFacility account."})

        # Only admins can view the verification details
        if requesting_ufacilityuser.is_admin == False:
            return Response({"status": status.HTTP_403_FORBIDDEN, "message": "User is neither a UFacility admin nor the owner of the verification."})

        # Check if verification exists
        if verification == None:
            return Response({"status": status.HTTP_404_NOT_FOUND, "message": "Verification does not exist."})

        serializer = VerificationSerializer(verification)
        return Response(serializer.data)

    def delete(self, request, verification_id):
        requesting_user = request.user
        requesting_ufacilityuser = UFacilityUser.objects.filter(user=requesting_user).first()
        verification = Verification.objects.filter(id=verification_id).first()

        # Check if requesting_user has a ufacility account
        if requesting_ufacilityuser == None:
            return Response({"status": status.HTTP_401_UNAUTHORIZED, "message": "User does not have a UFacility account."})

        # Only admins or the user itself can delete the verification
        if requesting_ufacilityuser.is_admin == False:
            return Response({"status": status.HTTP_403_FORBIDDEN, "message": "User is neither a UFacility admin nor the owner of the verification."})

        # Check if verification exists
        if verification == None:
            return Response({"status": status.HTTP_404_NOT_FOUND, "message": "Verification does not exist."})

        verification.delete()
        return Response({"status": status.HTTP_204_NO_CONTENT, "message": "Verification deleted."})

    def put(self, request, verification_id):
        requesting_user = request.user
        requesting_ufacilityuser = UFacilityUser.objects.filter(user=requesting_user).first()
        verification = Verification.objects.filter(id=verification_id).first()

        # Check if requesting_user has a ufacility account
        if requesting_ufacilityuser == None:
            return Response({"status": status.HTTP_401_UNAUTHORIZED, "message": "User does not have a UFacility account."})

        # Only admins or the user itself can delete the verification
        if requesting_ufacilityuser.is_admin == False:
            return Response({"status": status.HTTP_403_FORBIDDEN, "message": "User is neither a UFacility admin nor the owner of the verification."})

        # Check if verification exists
        if verification == None:
            return Response({"status": status.HTTP_404_NOT_FOUND, "message": "Verification does not exist."})

        data = request.data
        data["user"] = verification.user.id
        serializer = VerificationSerializer(verification, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid data."})


# GET, POST /bookings
class BookingView(APIView):
    def get(self, request):
        bookings = Booking.objects.all()
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request):
        requesting_user = request.user
        requesting_ufacilityuser = UFacilityUser.objects.filter(user=requesting_user).first()
        data = request.data
        data["user"] = requesting_ufacilityuser.id
        venue = Venue.objects.get(name=data["venue"])
        data["venue"] = venue.id
        data["status"] = "pending"

        if clash_exists(venue.id, data["date"], data["start_time"], data["end_time"]):
            return Response({"status": status.HTTP_409_CONFLICT, "message": "Booking clashes with another booking."})

        serializer = BookingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid data."})


# GET, PUT, DELETE /bookings/<booking_id>
class BookingDetailView(APIView):
    def get(self, request, booking_id):
        requesting_user = request.user
        requesting_ufacilityuser = UFacilityUser.objects.filter(user=requesting_user).first()
        booking = Booking.objects.filter(id=booking_id).first()

        # Check if requesting_user has a ufacility account
        if requesting_ufacilityuser == None:
            return Response({"status": status.HTTP_401_UNAUTHORIZED, "message": "User does not have a UFacility account."})

        # Check if booking exists
        if booking == None:
            return Response({"status": status.HTTP_404_NOT_FOUND, "message": "Booking does not exist."})

        # Viewing specific bookings is only allowed for admins and the user who created the booking
        if requesting_ufacilityuser.is_admin == False and requesting_ufacilityuser != booking.user:
            return Response({"status": status.HTTP_403_FORBIDDEN, "message": "User is neither a UFacility admin nor the owner of the booking."})

        serializer = BookingSerializer(booking)
        return Response(serializer.data)

    def put(self, request, booking_id):
        requesting_user = request.user
        requesting_ufacilityuser = UFacilityUser.objects.filter(user=requesting_user).first()
        booking = Booking.objects.filter(id=booking_id).first()

        # Check if requesting_user has a ufacility account
        if requesting_ufacilityuser == None:
            return Response({"status": status.HTTP_401_UNAUTHORIZED, "message": "User does not have a UFacility account."})

        # Check if booking exists
        if booking == None:
            return Response({"status": status.HTTP_404_NOT_FOUND, "message": "Booking does not exist."})

        # Updating bookings is only allowed for admins and the user who created the booking
        if requesting_ufacilityuser.is_admin == False and requesting_ufacilityuser != booking.user:
            return Response({"status": status.HTTP_403_FORBIDDEN, "message": "User is neither a UFacility admin nor the owner of the booking."})

        data = request.data
        venue = Venue.objects.get(name=data["venue"])
        data["venue"] = venue.id
        data["user"] = requesting_ufacilityuser.id
        data["status"] = booking.status
        serializer = BookingSerializer(booking, data=data, partial=True)
        if serializer.is_valid():
            if requesting_ufacilityuser.is_admin:
                email_subject = f"Booking request for {data['venue']} on {data['date']} from {data['start_time']} to {data['end_time']}"
                email_body = """\
                        This is an auto-generated email to inform you that a booking has been placed for {venue} on {date} from {start_time} to {end_time}.
                        Please contact {exco_email} should you have any enquiries.
                        """.format(venue=data["venue"], date=data["date"], start_time=data["start_time"], end_time=data["end_time"], exco_email=exco_email)
                send_email(email_subject, email_body, recipients=[venue.security_email])
            serializer.save()
            return Response(serializer.data)

        return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid data."})

    def delete(self, request, booking_id):
        requesting_user = request.user
        requesting_ufacilityuser = UFacilityUser.objects.filter(user=requesting_user).first()
        booking = Booking.objects.filter(id=booking_id).first()

        # Check if requesting_user has a ufacility account
        if requesting_ufacilityuser == None:
            return Response({"status": status.HTTP_401_UNAUTHORIZED, "message": "User does not have a UFacility account."})

        # Check if booking exists
        if booking == None:
            return Response({"status": status.HTTP_404_NOT_FOUND, "message": "Booking does not exist."})

        # Delete is only allowed for admins and the user who created the booking
        if requesting_ufacilityuser.is_admin == False and requesting_ufacilityuser != booking.user:
            return Response({"status": status.HTTP_403_FORBIDDEN, "message": "User is neither a UFacility admin nor the owner of the booking."})

        booking.delete()
        return Response({"status": status.HTTP_204_NO_CONTENT, "message": "Booking deleted."})


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
            return Response({"status": status.HTTP_401_UNAUTHORIZED, "message": "User does not have a UFacility account."})

        # POST is only allowed for admins
        if requesting_ufacilityuser.is_admin == False:
            return Response({"status": status.HTTP_403_FORBIDDEN, "message": "User is not a UFacility admin."})

        data = request.data
        serializer = VenueSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid data."})

