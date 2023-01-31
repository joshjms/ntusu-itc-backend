from django.contrib import admin
from .models import UFacilityUser, Venue, Booking2, Verification


class VerificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status',)


admin.site.register(Verification, VerificationAdmin)
admin.site.register(Booking2)
admin.site.register(Venue)
admin.site.register(UFacilityUser)
