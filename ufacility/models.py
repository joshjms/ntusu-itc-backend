from django.db import models
from django.core.validators import RegexValidator
from datetime import timedelta
from sso.models import User


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


def get_booking_path(instance, filename):
    return f'ufacility2/booking_file/{instance.id}/{filename}'


class AbstractBooking(models.Model):
    user = models.ForeignKey(UFacilityUser, on_delete=models.CASCADE)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    purpose = models.CharField(max_length=200)
    pax = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUSES)
    
    class Meta:
        abstract = True


class BookingGroup(AbstractBooking):
    class Frequency(models.TextChoices):
        EVERYDAY = 'ALL', 'Everyday'
        MONDAY = 'MON', 'Monday'
        TUESDAY = 'TUE', 'Tuesday'
        WEDNESDAY = 'WED', 'Wednesday'
        THURSDAY = 'THU', 'Thursday'
        FRIDAY = 'FRI', 'Friday'
        SATURDAY = 'SAT', 'Saturday'
        SUNDAY = 'SUN', 'Sunday'
    
    attachment = models.FileField(
        upload_to=get_booking_path,
        null=True, blank=True
    )
    created = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()
    recurring = models.CharField(max_length=3, choices=Frequency.choices)

    @property
    def venue_name(self):
        return self.venue.name

    @property
    def user_cca(self):
        return self.user.cca
    
    @property
    def user_email(self):
        return self.user.user.email
    
    @property
    def bookings(self):
        return [booking.id for booking in self.bookings.all()]

    @property
    def dates(self):
        date_mapping = {
            'MON': 0,
            'TUE': 1,
            'WED': 2,
            'THU': 3,
            'FRI': 4,
            'SAT': 5,
            'SUN': 6,
        }
        dates = []
        if self.recurring != 'ALL':
            target_day = date_mapping[self.recurring]
            curr_date = self.start_date
            while curr_date <= self.end_date:
                if curr_date.weekday() == target_day:
                    dates.append(curr_date)
                curr_date += timedelta(days=1)
        else:
            curr_date = self.start_date
            while curr_date <= self.end_date:
                dates.append(curr_date)
                curr_date += timedelta(days=1)
        return dates


class Booking2(AbstractBooking):
    booking_group = models.ForeignKey(BookingGroup, on_delete=models.CASCADE, related_name='bookings', null=True)
    date = models.DateField()

    @property
    def get_clashing_booking_id(self):
        clashes = Booking2.objects.filter(
            venue=self.venue,
            start_time__lt=self.end_time,
            end_time__gte=self.start_time,
        ).exclude(id=self.id).values_list("id", flat=True)
        return clashes

    def __str__(self) -> str:
        return f'<Booking ID {self.id}>: {self.venue} - {self.date} ({self.start_time} - {self.end_time})'


class Verification(AbstractUFacilityUser):
    status = models.CharField(max_length=8, choices=STATUSES)

    def __str__(self) -> str:
        return self.cca
