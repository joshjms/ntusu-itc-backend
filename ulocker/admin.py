from django.contrib import admin
from ulocker.models import Location, Booking, ULockerAdmin, Locker

# Register your models here.
admin.site.register(Location)
admin.site.register(Booking)
admin.site.register(ULockerAdmin)
admin.site.register(Locker)