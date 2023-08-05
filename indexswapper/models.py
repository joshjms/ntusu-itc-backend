from django.core.validators import (
    MinLengthValidator,
    MinValueValidator,
    MaxValueValidator,
)
from django.db import models
from indexswapper.utils.validation import ConvertibleListIndexValidator
from sso.models import User


class CourseIndex(models.Model):
    code = models.CharField(max_length=6)
    name = models.CharField(max_length=100)
    academic_units = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)])
    index = models.CharField(max_length=5, unique=True)
    datetime_added = models.DateTimeField(auto_now_add=True)
    information = models.TextField()
    pending_count = models.IntegerField(
        default=0, validators=[MinValueValidator(0)])

    @property
    def get_information(self):
        def serialize(msg):
            a = msg.split('^')
            return {
                'type': a[0], 'group': a[1],
                'day': a[2], 'time': a[3],
                'venue': a[4], 'remark': a[5]
            }
        return [serialize(x) for x in self.information.split(';')]

    class Meta:
        verbose_name_plural = 'Course Indexes'

    def __str__(self):
        return f'<Course Code {self.code}, Index {self.index}>'


class SwapRequest(models.Model):
    class Status(models.TextChoices):
        SEARCHING = 'S', 'Searching'
        WAITING = 'W', 'Waiting'
        COMPLETED = 'C', 'Completed'
        REVOKED = 'R', 'Revoked'

    class ContactType(models.TextChoices):
        EMAIL = 'E', 'Email'
        TELEGRAM = 'T', 'Telegram'
        PHONE = 'P', 'Phone'

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='swap_requests')
    contact_info = models.CharField(
        max_length=100, validators=[MinLengthValidator(5)])
    contact_type = models.CharField(
        max_length=1, choices=ContactType.choices)
    status = models.CharField(
        max_length=1,
        choices=Status.choices,
        default=Status.SEARCHING)
    datetime_added = models.DateTimeField(auto_now_add=True)
    datetime_found = models.DateTimeField(blank=True, null=True)
    current_index = models.ForeignKey(
        CourseIndex, on_delete=models.SET_NULL,
        related_name='available_swap', null=True)
    wanted_indexes = models.CharField(max_length=100)
    pair = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True)
    index_gained = models.CharField(max_length=6, default='', blank=True)

    @property
    def get_wanted_indexes(self):
        try:
            return eval(self.wanted_indexes)
        except:
            return []

    class Meta:
        verbose_name_plural = 'Swap Requests'

    def clean(self):
        validator = ConvertibleListIndexValidator(
            CourseIndex, self.current_index.code)
        validator(self.wanted_indexes)

    def __str__(self):
        return f'''<Swap Request #{self.id} by '{self.user.username}': \
{self.current_index.code} ({self.current_index.index} to {self.wanted_indexes})>'''
