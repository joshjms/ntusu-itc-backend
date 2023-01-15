from django.contrib import admin
from .models import UFacilityUser, Venue, Booking, Verification


admin.site.register(Verification)
admin.site.register(Booking)
admin.site.register(Venue)
admin.site.register(UFacilityUser)
