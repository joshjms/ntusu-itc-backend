from django.urls import path
from . import views


app_name='ulocker'

urlpatterns = [
    path('locker/', views.isBookedListView.as_view(), name='locker_is_booked_list'),
    path('booking/', views.UserBookingListView.as_view(), name='user_booking_list'),
    path('booking/<int:booking_id>/cancel/', views.BookingCancelView.as_view(), name='booking_cancel'),
    path('booking/<int:booking_id>/verify/', views.BookingVerifyView.as_view(), name='booking_verify'),
    path('config/', views.ULockerConfigView.as_view(), name='config'),
    
    path('booking/admin/', views.AdminBookingListView.as_view(), name='admin_booking_list'),
    path('change_booking_status/', views.ChangeBookingStatusView.as_view(), name='change_booking_status'),
    path('location/', views.LocationListView.as_view(), name='location'),
    path('locker/<int:location_id>/', views.LockerListView.as_view(), name='locker_list'),
]