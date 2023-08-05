from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from sso.models import User


# TODO - create user session ??? yes
# TODO - add ICC courses, ask for faculty when asking for swapping icc mod
# save contact details as session, cancelled request count, ban cooldown?
# class UserSession(models.Model):
#     user = models.OneToOneField(
#         User, on_delete=models.CASCADE,
#         related_name='index_swapper_session'
#     )
#     contact_info = models.CharField(max_length=100)
#     cancelled_request = models.IntegerField()

class IndexSwapperConfig(models.Model):
    web_scraper_link = models.CharField(max_length=200)
    
    class Meta:
        verbose_name_plural = 'Index Swapper Configuration'

    def save(self, *args, **kwargs):
        if IndexSwapperConfig.objects.exists():
            raise ValidationError('There can only be 1 IndexSwapperConfig instance!')
        return super().save(*args, **kwargs)


class XCourseIndex(models.Model):
    code = models.CharField(max_length=6)
    name = models.CharField(max_length=100)
    academic_units = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)]
    )
    index = models.CharField(max_length=5, unique=True)
    datetime_added = models.DateTimeField(auto_now_add=True)
    information = models.TextField()
    pending_count = models.IntegerField(default=0)

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


class XSwapRequest(models.Model):
    class Status(models.TextChoices):
        SEARCHING = 'S', 'Searching'
        WAITING = 'W', 'Waiting'
        COMPLETED = 'C', 'Completed'
    
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='Xswap_requests'
    )
    contact_info = models.CharField(max_length=100)
    status = models.CharField(
        max_length=1,
        choices=Status.choices,
        default=Status.SEARCHING
    )
    datetime_added = models.DateTimeField(auto_now_add=True)
    datetime_found = models.DateTimeField(blank=True, null=True)
    current_index = models.ForeignKey(
        XCourseIndex, on_delete=models.SET_NULL,
        related_name='Xavailable_swap', null=True
    )
    wanted_indexes = models.CharField(max_length=100)

    @property
    def get_wanted_indexes(self):
        return self.wanted_indexes.split(';')
    
    class Meta:
        verbose_name_plural = 'Swap Requests'
    
    def __str__(self):
        return f'''<Swap Request by '{self.user.username}':
            {self.current_index.code} ({self.current_index.index}
            to {self.wanted_indexes})>
        '''
