from django.db import models
from sso.models import User
from django.core.validators import RegexValidator


STATUSES = (
    ("pending", "Pending"),
    ("accepted", "Accepted"),
    ("declined", "Declined"),
)


validate_singapore_phone_number = RegexValidator(
    regex=r'^[689]\d{7}$',
    message='Singapore phone number required (8 digits, without the +65)'
)


class AbstractUFacilityUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    cca = models.CharField(max_length=30)
    hongen_name = models.CharField(max_length=30)
    hongen_phone_number = models.CharField(max_length=8,
        validators=[validate_singapore_phone_number])
    
    class Meta:
        abstract = True


class UFacilityUser(AbstractUFacilityUser):
    is_admin = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.user.display_name


class Venue(models.Model):
    name = models.CharField(max_length=30, unique=True)
    security_email = models.EmailField(max_length=50)

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
        return f"<Booking ID {self.id}>: {self.venue} - {self.date} ({self.start_time} - {self.end_time})"


class Verification(AbstractUFacilityUser):
    status = models.CharField(max_length=8, choices=STATUSES)

    def __str__(self) -> str:
        return self.cca
