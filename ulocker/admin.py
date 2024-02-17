from django.contrib import admin
from ulocker.models import Location, Booking, ULockerAdmin

# Register your models here.
admin.site.register(Location)
admin.site.register(Booking)
admin.site.register(ULockerAdmin)
