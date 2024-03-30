from django.contrib import admin
from django.db.models import Count
from ulocker.models import Location, Booking, ULockerAdmin, Locker
from ulocker.utils import LockerStatusUtils as LSU, ULockerEmailService


class LocationAdmin(admin.ModelAdmin):
    list_display = ['id', 'location_name', 'locker_count']
    ordering = ['id']
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(locker_count=Count('locker'))
        return queryset

    def locker_count(self, obj):
        return obj.locker_count
    
    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['__str__', 'location_name', 'locker_count']
        return readonly_fields

class LockerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'location', 'passcode', 'is_available', 'status']
    ordering = ['id']

    def status(self, obj):
        queryset = LSU.get_locker_status([obj])
        return queryset[0].status
    
    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['__str__', 'name', 'location']
        return readonly_fields

class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'location_name', 'locker_name', 'user_email', 'applicant_name', 'start_month', 'duration', 'status', 'creation_date']

    def location_name(self, obj):
        return obj.locker.location.location_name
    
    def locker_name(self, obj):
        return obj.locker.name
    
    def user_email(self, obj):
        return obj.user.email
    
    def save_model(self, request, obj, form, change):
        if change and form.initial['status'] != Booking.AllocationStatus.AWAITING_PAYMENT \
                and obj.status == Booking.AllocationStatus.AWAITING_PAYMENT:
            ULockerEmailService.send_payment_email(obj)
        elif change and form.initial['status'] != Booking.AllocationStatus.ALLOCATED \
                and obj.status == Booking.AllocationStatus.ALLOCATED:
            ULockerEmailService.send_allocation_email(obj)
        super().save_model(request, obj, form, change)

class ULockerAdminAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'user_email']
    
    def user_email(self, obj):
        return obj.user.email

admin.site.register(Location, LocationAdmin)
admin.site.register(Locker, LockerAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(ULockerAdmin, ULockerAdminAdmin)
