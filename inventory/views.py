from rest_framework import status
from rest_framework import generics, viewsets, permissions
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import render

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
class ItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        serializer.save(user=self.request.user.inventorylender)
    
# view all loan requests // this one for admin only
class ItemLoanRequestListView(generics.ListAPIView):
    serializer_class = ItemLoanRequestSerializer
    queryset = ItemLoanRequest.objects.all()
    
# view the user loan requests
class UserLoanRequestListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ItemLoanRequestSerializer
    
    def get_queryset(self):
        user_id = self.request.user.id
        # checking the request user and the token user
        if self.kwargs['username'] != self.request.user.username:
            return Response({"detail": "You are not authorized to view this user's loan requests"}, status=status.HTTP_401_UNAUTHORIZED)
        return ItemLoanRequest.objects.filter(user=user_id)
    
# send loan request
class LoanRequestCreateView(generics.CreateAPIView):
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
class LoanRequestReturnView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request, pk, *args, **kwargs):
        try:
            request_user = InventoryUser.objects.get(pk=request.user.id)
            loan_request = ItemLoanRequest.objects.get(pk=pk, user=request_user)
        except ItemLoanRequest.DoesNotExist:
            return Response({"detail": "Loan request not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if loan_request.approval_status != 'accepted':
            return Response({"detail": "Loan request has not been accepted"}, status=status.HTTP_400_BAD_REQUEST)
        
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
        
        item_serializer = ItemSerializer(item)
        return Response({"detail": "Item returned successfully", "item": item_serializer.data}, status=status.HTTP_200_OK)
