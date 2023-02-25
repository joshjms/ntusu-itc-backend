from django.urls import path
from . import views


app_name = 'ufacility'
urlpatterns = [
    

    path('verifications/', views.VerificationView.as_view(), name='verifications'),
    path('verifications/<int:verification_id>/', views.VerificationDetailView.as_view(), name='verification-detail'),


    path('bookings/<int:venue_id>/<str:date>/', views.BookingHourlyView.as_view(), name='booking-hourly'),
    path('venues/', views.VenueView.as_view(), name='venues'),
    path('venues/<int:venue_id>/', views.VenueDetailView.as_view(), name='venue-detail'),

    path('booking_group/', views.BookingGroupView.as_view(), name='booking-group'),
    path('booking_group/admin/', views.BookingGroupAdminView.as_view(), name='booking-group-admin'),
    path('booking_group/<int:bookinggroup_id>/', views.BookingGroupDetailView.as_view(), name='booking-group-detail'),
    path('booking_group/<int:bookinggroup_id>/accept/', views.BookingGroupAcceptView.as_view(), name='booking-group-accept'),
    path('booking_group/<int:bookinggroup_id>/reject/', views.BookingGroupRejectView.as_view(), name='booking-group-reject'),
    path('check_user_status/', views.CheckStatusView.as_view(), name='check-user-status'),
    path('users/<int:user_id>/', views.UFacilityUserDetailView.as_view(), name='user-detail'),
    path('verifications/<int:verification_id>/accept/', views.VerificationAcceptView.as_view(), name='verification-accept'),
    path('verifications/<int:verification_id>/reject/', views.VerificationRejectView.as_view(), name='verification-reject'),
]
