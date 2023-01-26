from ufacility.models import Verification, Booking, Venue, UFacilityUser
from rest_framework import serializers


class UFacilityUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UFacilityUser
        fields = ["id", "user", "is_admin", "cca", "role", "status"]
        
    def create(self, validated_data):
        validated_data["is_admin"] = False
        validated_data["status"] = "pending"
        ufacilityuser = UFacilityUser.objects.create(**validated_data)
        return ufacilityuser


class VerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Verification
        fields = ["id", "user", "email", "cca", "role"]

    def create(self, validated_data):
        verification = Verification.objects.create(**validated_data)
        return verification

    def update(self, instance, validated_data):
        instance.email = validated_data.get("email", instance.email)
        instance.cca = validated_data.get("cca", instance.cca)
        instance.role = validated_data.get("role", instance.role)
        instance.save()
        return instance


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["id", "user", "venue", "start_time", "end_time", "purpose", "pax", "status"]

    def create(self, validated_data):
        booking = Booking.objects.create(**validated_data)
        return booking

    def update(self, instance, validated_data):
        instance.venue = validated_data.get("venue", instance.venue)
        instance.start_time = validated_data.get("start_time", instance.start_time)
        instance.end_time = validated_data.get("end_time", instance.end_time)
        instance.purpose = validated_data.get("purpose", instance.purpose)
        instance.pax = validated_data.get("pax", instance.pax)
        instance.status = validated_data.get("status", instance.status)
        instance.save()
        return instance


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = ["id", "name", "security_email"]

    def create(self, validated_data):
        venue = Venue.objects.create(**validated_data)
        return venue
