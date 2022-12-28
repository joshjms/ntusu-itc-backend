from django.urls import path
from . import views


app_name = 'ufacility'
urlpatterns = [
    path("users/", views.UserView.as_view(), name="users"),
    path("users/<int:user_id>/", views.UserDetailView.as_view(), name="user-detail"),
    path("verifications/", views.VerificationView.as_view(), name="verifications"),
    path("verifications/<int:verification_id>/", views.VerificationDetailView.as_view(), name="verification-detail"),
    path("bookings/", views.BookingView.as_view(), name="bookings"),
    path("bookings/<int:booking_id>/", views.BookingDetailView.as_view(), name="booking-detail"),
    path("venues/", views.VenueView.as_view(), name="venues"),
]
