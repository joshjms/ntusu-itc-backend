from django.urls import path

from .views import (
    InventoryItemListView,
    InventoryItemDetailView,
    InventoryBookingListView,
    InventoryBookingCreateView,
    InventoryBookingReturnView,
    UserInventoryBookingListView,
)

app_name = 'inventory'
urlpatterns = [
    path('items/', InventoryItemListView.as_view(), name='item-list'),
    path('items/<int:pk>/', InventoryItemDetailView.as_view(), name='item-detail'),
    path('bookings/', InventoryBookingListView.as_view(), name='loan-requests'),
    path('bookings/<str:username>/', UserInventoryBookingListView.as_view(), name='user-loan-requests'),
    path('items/loan/', InventoryBookingCreateView.as_view(), name='loan-request-create'),
    path('bookings/return/<int:pk>', InventoryBookingReturnView.as_view(), name='loan-request-return'),
]
