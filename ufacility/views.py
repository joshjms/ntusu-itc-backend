from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from ufacility.models import Verification, Booking, Venue, UFacilityUser
from ufacility.serializers import VerificationSerializer, BookingSerializer, VenueSerializer, UFacilityUserSerializer
from sso.models import User


# POST /users
class UserView(APIView):
    def post(self, request):
        user = request.user
        ufacilityuser = UFacilityUser.objects.get(user=user)

        # Check if user exists
        if ufacilityuser == None:
            return Response({"status": "ufacilityuser does not exist"})
        
        # Only admins can create users
        if ufacilityuser.is_admin == False:
            return Response({"status": "unauthorized"})

        data = request.data
        serializer = UFacilityUserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors)


# GET /users/<user_id>
class UserDetailView(APIView):
    def get(self, request, user_id):
        ufacilityuser = UFacilityUser.objects.get(id=user_id)
        # Check if user exists
        if ufacilityuser == None:
            return Response({"status": "ufacilityuser does not exist"})

        requesting_user = request.user
        requesting_ufacilityuser = UFacilityUser.objects.get(user=requesting_user)
        # Only admins or the user itself can view the user details
        if requesting_ufacilityuser != ufacilityuser and requesting_ufacilityuser.is_admin == False:
            return Response({"status": "unauthorized"})

        serializer = UFacilityUserSerializer(ufacilityuser)
        return Response(serializer.data)


# GET, POST /verifications
class VerificationView(APIView):
    def get(self, request):
        user = request.user
        ufacilityuser = UFacilityUser.objects.get(user=user)

        # Only admins can view all verifications
        if ufacilityuser.is_admin == False:
            return Response({"status": "unauthorized"})

        verifications = Verification.objects.all()
        serializer = VerificationSerializer(verifications, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = request.user

        data = request.data
        data["user"] = user.id
        serializer = VerificationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors)


# GET, DELETE /verifications/<verification_id>
class VerificationDetailView(APIView):
    def get(self, request, verification_id):
        user = request.user
        ufacilityuser = UFacilityUser.objects.get(user=user)
        verification = Verification.objects.get(id=verification_id)

        # Check if verification exists
        if verification == None:
            return Response({"status": "verification does not exist"})

        # Only admins or the user itself can view the verification details
        if verification.user != user and ufacilityuser.is_admin == False:
            return Response({"status": "unauthorized"})

        serializer = VerificationSerializer(verification)
        return Response(serializer.data)

    def delete(self, request, verification_id):
        user = request.user
        ufacilityuser = UFacilityUser.objects.get(user=user)
        verification = Verification.objects.get(id=verification_id)

        # Check if verification exists
        if verification == None:
            return Response({"status": "verification does not exist"})

        # Only admins or the user itself can delete the verification
        if verification.user != ufacilityuser and ufacilityuser.is_admin == False:
            return Response({"status": "unauthorized"})

        verification.delete()
        return Response({"status": "deleted"})

    def put(self, request, verification_id):
        user = request.user
        ufacilityuser = UFacilityUser.objects.get(user=user)
        verification = Verification.objects.get(id=verification_id)

        # Check if verification exists
        if verification == None:
            return Response({"status": "verification does not exist"})

        # Only admins or the user itself can update the verification
        if verification.user != ufacilityuser and ufacilityuser.is_admin == False:
            return Response({"status": "unauthorized"})

        data = request.data
        data["user"] = verification.user.id
        serializer = VerificationSerializer(verification, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors)


# GET, POST /bookings
class BookingView(APIView):
    def get(self, request):
        user = request.user
        ufacilityuser = UFacilityUser.objects.get(user=user)
        if ufacilityuser.is_admin == True:
            bookings = Booking.objects.all()
            serializer = BookingSerializer(bookings, many=True)
            return Response(serializer.data)
        else:
            bookings = Booking.objects.filter(status="accepted")
            serializer = BookingSerializer(bookings, many=True)
            return Response(serializer.data)

    def post(self, request):
        user = request.user
        data = request.data
        ufacilityuser = UFacilityUser.objects.get(user=user)
        data["user"] = ufacilityuser.id
        venue = Venue.objects.get(name=data["venue"])
        data["venue"] = venue.id
        data["status"] = "pending"
        serializer = BookingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors)


# GET, PUT, DELETE /bookings/<booking_id>
class BookingDetailView(APIView):
    def get(self, request, booking_id):
        booking = Booking.objects.get(id=booking_id)
        if booking == None:
            return Response({"status": "booking does not exist"})

        serializer = BookingSerializer(booking)
        return Response(serializer.data)

    def put(self, request, booking_id):
        user = request.user
        ufacilityuser = UFacilityUser.objects.get(user=user)
        booking = Booking.objects.get(id=booking_id)

        # Check if booking exists
        if booking == None:
            return Response({"status": "booking does not exist"})

        # Update is only allowed for admins and the user who created the booking
        if ufacilityuser.is_admin == False and booking.user != ufacilityuser:
            return Response({"status": "unauthorized"})

        data = request.data
        venue = Venue.objects.get(name=data["venue"])
        data["venue"] = venue.id
        data["user"] = ufacilityuser.id
        data["status"] = booking.status
        serializer = BookingSerializer(booking, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors)

    def delete(self, request, booking_id):
        user = request.user
        ufacilityuser = UFacilityUser.objects.get(user=user)
        booking = Booking.objects.get(id=booking_id)

        # Delete is only allowed for admins and the user who created the booking
        if ufacilityuser.is_admin == False and booking.user != ufacilityuser:
            return Response({"status": "unauthorized"})

        booking.delete()
        return Response({"status": "booking deleted"})


# GET, POST /venues
class VenueView(APIView):
    def get(self, request):
        venues = Venue.objects.all()
        serializer = VenueSerializer(venues, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        ufacilityUser = UFacilityUser.objects.get(user=user)

        # POST is only allowed for admins
        if ufacilityUser.is_admin == False:
            return Response({"status": "unauthorized"})

        data = request.data
        serializer = VenueSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors)
