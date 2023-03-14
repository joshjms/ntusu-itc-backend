from django.contrib import admin
from .models import UFacilityUser, Venue, Booking2, Verification, BookingGroup, SecurityEmail


class VerificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status',)


class UFacilityUserAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__',)


class BookingGroupAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'status')


class BookingAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'status')


class VenueAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'is_send_security_mail')


admin.site.register(Verification, VerificationAdmin)
admin.site.register(Booking2, BookingAdmin)
admin.site.register(BookingGroup, BookingGroupAdmin)
admin.site.register(Venue, VenueAdmin)
admin.site.register(UFacilityUser, UFacilityUserAdmin)
admin.site.register(SecurityEmail)
