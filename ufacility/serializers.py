from rest_framework import serializers
from ufacility.models import Verification, Booking2, Venue, UFacilityUser
from sso.serializers import UserProfileSerializer


class UFacilityUserSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(many=False, read_only=True)
    
    class Meta:
        model = UFacilityUser
        fields = ["id", "user", "is_admin", "cca", "hongen_name", "hongen_phone_number"]
        
    def create(self, validated_data):
        validated_data["is_admin"] = False
        ufacilityuser = UFacilityUser.objects.create(**validated_data)
        return ufacilityuser


class VerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Verification
        fields = ["id", "user", "cca", "hongen_name", "hongen_phone_number", "status"]

    def create(self, validated_data):
        verification = Verification.objects.create(**validated_data)
        return verification

    def update(self, instance, validated_data):
        instance.cca = validated_data.get("cca", instance.cca)
        instance.hongen_name = validated_data.get("hongen_name", instance.hongen_name)
        instance.hongen_phone_number = validated_data.get("hongen_phone_number", instance.hongen_phone_number)
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


class BookingSerializer(serializers.ModelSerializer):
    user = UFacilityUserSerializer(many=False)
    venue = VenueSerializer(many=False)

    class Meta:
        model = Booking2
        fields = ["id", "user", "venue", "date", "start_time", "end_time", "purpose", "pax", "status"]
        read_only_fields = ['id', 'user', 'status']

    def create(self, validated_data):
        booking = Booking2.objects.create(**validated_data)
        return booking
