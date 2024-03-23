from django.urls import path
from . import views

app_name="ulocker"

urlpatterns = [
    path('booking/', views.UserBookingListView.as_view(), name='user_booking_list'),
    path('booking/admin/', views.AdminBookingListView.as_view(), name='admin_booking_list'),
    path('change_booking_status/', views.ChangeBookingStatusView.as_view(), name='change_booking_status'),
    path('change_payment_status/', views.ChangePaymentStatusView.as_view(), name='change_payment_status'),
]
