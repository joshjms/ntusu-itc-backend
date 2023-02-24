from django.contrib import admin
from event.models import Event, EventAdmin, EventOfficer, MatricCheckIn

# Register your models here.
admin.site.register(Event)
admin.site.register(EventAdmin)
admin.site.register(EventOfficer)
admin.site.register(MatricCheckIn)