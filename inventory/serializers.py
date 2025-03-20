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
    item = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all())
    class Meta:
        model = ItemLoanRequest
        fields = '__all__' # Include all fields in the API
        read_only_fields = ['id', 'user']
