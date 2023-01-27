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
    _is_active = models.BooleanField(default=False)
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
    def is_active(self) -> bool:
        from django.utils import timezone as tz
        current_time = tz.now()

        if self.start_time <= current_time and self.auto_start == True:
            self.auto_start = False
            self._is_active = True

        if self.end_time <= current_time and self.auto_end == True:
            self.auto_end = False
            self._is_active = False

        self.save()
        return self._is_active