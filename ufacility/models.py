from django.db import models
from sso.models import User


STATUSES = (
    ("pending", "Pending"),
    ("accepted", "Accepted"),
    ("declined", "Declined"),
)


class UFacilityUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    is_admin = models.BooleanField(default=False)
    cca = models.CharField(max_length=100)
    hongen_name = models.CharField(max_length=100, default='')
    hongen_phone_number = models.CharField(max_length=100, default='')

    def __str__(self) -> str:
        return self.user.display_name


class Venue(models.Model):
    name = models.CharField(max_length=100, unique=True)
    security_email = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Booking2(models.Model):
    user = models.ForeignKey(UFacilityUser, on_delete=models.CASCADE)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    purpose = models.CharField(max_length=200)
    pax = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUSES)

    def __str__(self) -> str:
        return f"{self.venue} {self.date} {self.start_time} - {self.end_time}"


class Verification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    cca = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUSES)
    hongen_name = models.CharField(max_length=100)
    hongen_phone_number = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.cca
