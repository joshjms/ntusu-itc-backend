from django.db import models
from sso.models import User
from django.utils import timezone as tz

class EventAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    is_superadmin = models.BooleanField(default=False)
    def __str__(self):
        return self.user.username

class Event(models.Model):
    name = models.CharField(max_length=100)
    added_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    allow_non_undergraduate = models.BooleanField(default=True)
    allow_exchange_student = models.BooleanField(default=True)
    event_admin = models.ForeignKey(EventAdmin, on_delete=models.CASCADE, related_name="events")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    auto_start = models.BooleanField(default=True)
    auto_end = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    @property
    def check_is_active(self) -> bool:
        current_time = tz.now()

        if self.start_time <= current_time and self.auto_start == True:
            self.auto_start = False
            self._is_active = True

        if self.end_time <= current_time and self.auto_end == True:
            self.auto_end = False
            self._is_active = False

        self.save()
        return self._is_active


class EventOfficer(models.Model):
    event = models.ForeignKey(Event, on_delete = models.CASCADE, related_name = "officers")
    added_date = models.DateTimeField(auto_now_add = True)
    token =  models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.name} - {self.token}"

class MatricCheckIn(models.Model):
    matric_number = models.CharField(max_length=100)
    event = models.ForeignKey(Event, on_delete = models.CASCADE, related_name ="matric_checked_in" )
    added_date = models.DateTimeField(auto_now_add = True)
    officer_name = models.CharField(max_length=100)
    def __str__(self):
        return self.matric_number

