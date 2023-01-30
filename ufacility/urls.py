from django.urls import path
from . import views


app_name = 'ufacility'
urlpatterns = [
    path("users/", views.UserView.as_view(), name="users"),
    path("users/<int:user_id>/", views.UserDetailView.as_view(), name="user-detail"),
    path("users/<int:user_id>/bookings/", views.UserBookingsView.as_view(), name="user-bookings"),
    path("verifications/", views.VerificationView.as_view(), name="verifications"),
    path("verifications/<int:verification_id>/", views.VerificationDetailView.as_view(), name="verification-detail"),
    path("bookings/", views.BookingView.as_view(), name="bookings"),
    path("bookings/<int:booking_id>/", views.BookingDetailView.as_view(), name="booking-detail"),
    path('bookings/<int:booking_id>/accept/', views.AcceptBookingView.as_view(), name='booking-accept'),
    path('bookings/<int:booking_id>/reject/', views.RejectBookingView.as_view(), name='booking-reject'),
    path('venues/', views.VenueView.as_view(), name='venues'),
    path('venues/<int:venue_id>/', views.VenueDetailView.as_view(), name='venues-detail'),
]
