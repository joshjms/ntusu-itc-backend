from django.shortcuts import render
from rest_framework import status
from rest_framework import generics, viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.utils import timezone

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
    
# send loan request
class LoanRequestCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        item_id = request.data.get('item')
        quantity = request.data.get('quantity')
        user_id = request.user.id
        
        try:
            item = Item.objects.get(pk=item_id)
        except Item.DoesNotExist:
            return Response({"Item not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if item.quantity < quantity:
            return Response({"detail": "Not enough items available"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ItemLoanRequestSerializer(data=request.data)
        if serializer.is_valid():
            request_user = InventoryUser.objects.get(pk=user_id)
            serializer.save(user=request_user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# return item
class LoanRequestReturnView(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request, pk, *args, **kwargs):
        try:
            request_user = InventoryUser.objects.get(pk=request.user.id)
            loan_request = ItemLoanRequest.objects.get(pk=pk, user=request_user)
        except ItemLoanRequest.DoesNotExist:
            return Response({"detail": "Loan request not found"}, status=status.HTTP_404_NOT_FOUND)
        
        loan_request.return_date = timezone.now()
        loan_request.approval_status = 'returned'
        loan_request.save()
        
        # increase item quantity
        try:
            item = Item.objects.get(pk=loan_request.item.id)
            item.quantity += loan_request.quantity
            item.save()
        except Item.DoesNotExist:
            return Response({"detail": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({"detail": "Item returned successfully"}, status=status.HTTP_200_OK)