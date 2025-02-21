from django.shortcuts import render
from rest_framework import generics
from rest_framework import viewsets

from .models import (
    InventoryUser, 
    InventoryLender, 
    Item, 
    ItemLoanRequest
)

from .serializers import (
    InventoryUserSerializer,
    InventoryLenderSerializer,
    ItemSerializer,
    ItemLoanRequestSerializer,
)

# view items
class ItemListView(generics.ListAPIView):
    serializer_class = ItemSerializer
    queryset = Item.objects.all()