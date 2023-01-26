from django.contrib import admin
from .models import UFacilityUser, Venue, Booking2, Verification


admin.site.register(Verification)
admin.site.register(Booking2)
admin.site.register(Venue)
admin.site.register(UFacilityUser)
