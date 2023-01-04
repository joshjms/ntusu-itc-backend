from django.db import models
from django.core.exceptions import ValidationError
from sso.models import User


# TODO - create user session ???
# save contact details as session, cancelled request count, ban cooldown?

# class IndexSwapperConfig(models.Model):
#     web_scraper_link = models.CharField(max_length=200)

#     def save(self, *args, **kwargs):
#         if IndexSwapperConfig.objects.exists():
#             raise ValidationError('There can only be 1 IndexSwapperConfig instance!')
#         return super().save(*args, **kwargs)


class CourseIndex(models.Model):
    code = models.CharField(max_length=6)
    name = models.CharField(max_length=100)
    index = models.CharField(max_length=5, unique=True)
    datetime_added = models.DateTimeField(auto_now_add=True)
    information = models.TextField()
    pending_count = models.IntegerField(default=0)

    @property
    def get_information(self):
        def serialize(msg):
            a = msg.split('\\')
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
    
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='swap_requests'
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
        CourseIndex, on_delete=models.CASCADE,
        related_name='available_swap'
    )
    wanted_indexes = models.CharField(max_length=100)

    @property
    def get_wanted_indexes(self):
        pass # TODO

    class Meta:
        verbose_name_plural = 'Swap Requests'
    
    def __str__(self):
        return f'''<Swap Request by '{self.user.username}':
            {self.current_index.code} ({self.current_index.index}
            to {self.wanted_indexes})>
        '''
