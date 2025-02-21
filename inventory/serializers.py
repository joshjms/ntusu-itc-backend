from rest_framework import serializers
from inventory.models import InventoryUser, InventoryLender, Item, ItemLoanRequest

class InventoryUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryUser
        fields = ['user.id', 'user.username', 'user.email']

class InventoryLenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryLender
        fields = ['user.id', 'user.username', 'user.email', 'organisation_name']

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'title', 'description', 'category', 'attachment', 'quantity', 'user']

class ItemLoanRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemLoanRequest
        fields = ['id', 'approval_status', 'start_date', 'end_date', 'return_date', 'quantity', 'item', 'user']

