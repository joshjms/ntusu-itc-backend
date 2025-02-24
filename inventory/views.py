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
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    
# view item with id
class ItemDetailView(generics.RetrieveAPIView):
    serializer_class = ItemSerializer
    queryset = Item.objects.all()
    lookup_url_kwarg = 'item_id'
    
# view all loan requests
class ItemLoanRequestListView(generics.ListAPIView):
    serializer_class = ItemLoanRequestSerializer
    queryset = ItemLoanRequest.objects.all()
    
# borrow item with id
class BorrowItemView(generics.RetrieveAPIView):
    serializer_class = ItemSerializer
    queryset = Item.objects.all()