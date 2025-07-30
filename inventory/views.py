from rest_framework import status
from rest_framework import generics, viewsets, permissions
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import render

from inventory.models import (
    InventoryBooking,
    InventoryItem,
    InventoryUser,
    InventoryLender,
)

from inventory.serializers import (
    InventoryBookingSerializer,
    InventoryItemSerializer,
    InventoryLenderSerializer,
    InventoryUserSerializer,
)

class InventoryItemListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer

class InventoryItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        serializer.save(user=self.request.user.inventorylender)

class InventoryBookingListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InventoryBookingSerializer
    queryset = InventoryBooking.objects.all()

class UserInventoryBookingListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InventoryBookingSerializer
    
    def get_queryset(self):
        user_id = self.request.user.id
        # checking the request user and the token user
        if self.kwargs['username'] != self.request.user.username:
            return Response({"detail": "You are not authorized to view this user's bookings"}, status=status.HTTP_401_UNAUTHORIZED)
        return InventoryBooking.objects.filter(user=user_id)

class InventoryBookingCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        item_id = request.data.get('item')
        quantity = request.data.get('quantity')
        user_id = request.user.id
        
        try:
            item = InventoryItem.objects.get(pk=item_id)
        except InventoryItem.DoesNotExist:
            return Response({"Item not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if item.quantity < quantity:
            return Response({"detail": "Not enough items available"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = InventoryBookingSerializer(data=request.data)
        if serializer.is_valid():
            request_user = InventoryUser.objects.get(pk=user_id)
            serializer.save(user=request_user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InventoryBookingReturnView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request, pk, *args, **kwargs):
        try:
            request_user = InventoryUser.objects.get(pk=request.user.id)
            booking = InventoryBooking.objects.get(pk=pk, user=request_user)
        except InventoryBooking.DoesNotExist:
            return Response({"detail": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if booking.approval_status != 'accepted':
            return Response({"detail": "Booking has not been accepted"}, status=status.HTTP_400_BAD_REQUEST)
        
        booking.return_date = timezone.now()
        booking.approval_status = 'returned'
        booking.save()
        
        try:
            item = InventoryItem.objects.get(pk=booking.item.id)
            item.quantity += booking.quantity
            item.save()
        except InventoryItem.DoesNotExist:
            return Response({"detail": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        
        item_serializer = InventoryItemSerializer(item)
        return Response({"detail": "Item returned successfully", "item": item_serializer.data}, status=status.HTTP_200_OK)
