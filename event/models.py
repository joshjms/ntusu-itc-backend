from django.db import models
from sso.models import User

class EventAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    is_superadmin = models.BooleanField(default=False)
    def __str__(self):
        return self.user.username

class Event(models.Model):
    name = models.CharField(max_length=100)
    added_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    allow_non_undergraduate = models.BooleanField(default=True)
    allow_exchange_student = models.BooleanField(default=True)
    event_admin = models.ForeignKey(EventAdmin, on_delete=models.CASCADE, related_name="events")
    start_time = models.DateField()
    end_time = models.DateField()
    def __str__(self):
        return self.name

class EventOfficer(models.Model):
    event = models.ForeignKey(Event, on_delete= models.CASCADE)
    added_date = models.DateTimeField(auto_now_add = True)
    token =  models.CharField()
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)
    def __str__(self):
        return self.name

class MatricCheckIn(models.Model):
    matric_number = models.CharField()
    event = models.ForeignKey(Event, on_delete = models.CASCADE)
    added_date = models.DateTimeField(auto_now_add = True)
    officer_name = models.CharField(max_length=100)
    def __str__(self):
        return self.matric_number
        