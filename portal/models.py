from django.db import models
from django.utils import timezone as tz


class UpdateNote(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=250)
    content = models.TextField()
    added = models.DateTimeField(default=tz.now)
    public = models.BooleanField(default=False)

    def __str__(self):
        return f'<Update {self.id} (public={self.public}): {self.title}>'


class FeedbackForm(models.Model):
    class Type(models.TextChoices):
        BUG_REPORT = 'Bug Report', 'Bug Report'
        FEATURE_REQUEST = 'Feature Request', 'Feature Request'
        IMPROVEMENT_SUGGESTION = 'Improvement Suggestion', 'Improvement Suggestion'
        REQUEST_ASSISTANCE = 'Request Assistance', 'Request Assistance'
        ITC_RECRUITMENT = 'ITC Recruitment', 'ITC Recruitment'
        OTHERS = 'Others', 'Others'

    type = models.CharField(max_length=30, choices=Type.choices)
    title = models.CharField(max_length=100)
    details = models.TextField()
    email = models.EmailField(max_length=100, blank=True)
    acknowledged = models.BooleanField(default=False)
    resolved = models.BooleanField(default=False)
    response = models.TextField(blank=True)
    time = models.DateTimeField(default=tz.now)

    def __str__(self):
        return f'<FeedbackForm {self.id}: ({self.type}) {self.title}>'
