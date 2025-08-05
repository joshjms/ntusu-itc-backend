from rest_framework import serializers
from inventory.models import InventoryUser, InventoryLender, InventoryItem, InventoryBooking

class InventoryUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryUser
        fields = ['user.id', 'user.username', 'user.email']

class InventoryLenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryLender
        fields = ['user.id', 'user.username', 'user.email', 'organisation_name']

class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = ['id', 'title', 'description', 'category', 'attachment', 'quantity', 'user']

class InventoryBookingSerializer(serializers.ModelSerializer):
    item = serializers.PrimaryKeyRelatedField(queryset=InventoryItem.objects.all())
    class Meta:
        model = InventoryBooking
        fields = '__all__' # Include all fields in the API
        read_only_fields = ['id', 'user']
