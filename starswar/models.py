from django.db import models
from sso.models import User


# TODO - create user session


class CourseIndex(models.Model):
    code = models.CharField(max_length=6)
    name = models.CharField(max_length=100)
    index = models.CharField(max_length=5, unique=True)
    datetime_added = models.DateTimeField(auto_now_add=True)
    information = models.TextField()
    pending_count = models.IntegerField(default=0)

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

    class Meta:
        verbose_name_plural = 'Swap Requests'
    
    def __str__(self):
        return f'''<Swap Request by '{self.user.username}':
            {self.current_index.code} ({self.current_index.index}
            to {self.wanted_indexes})>
        '''
