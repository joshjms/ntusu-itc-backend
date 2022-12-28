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
    role = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUSES)

    def __str__(self) -> str:
        return self.user.display_name


class Venue(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.name


class Booking(models.Model):
    user = models.ForeignKey(UFacilityUser, on_delete=models.CASCADE)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    date = models.DateField()
    purpose = models.CharField(max_length=200)
    pax = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUSES)

    def __str__(self) -> str:
        return f"{self.venue} {self.date} {self.start_time} - {self.end_time}"


class Verification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    email = models.CharField(max_length=100, unique=True)
    cca = models.CharField(max_length=100)
    role = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.email
