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
        BUG_REPORT = 'BR', 'Bug Report'
        FEATURE_REQUEST = 'FR', 'Feature Request'
        IMPROVEMENT_SUGGESTION = 'IS', 'Improvement Suggestion'
        REQUEST_ASSISTANCE = 'RA', 'Request Assistance'
        ITC_RECRUITMENT = 'IR', 'ITC Recruitment'
        OTHERS = 'OT', 'Others'

    type = models.CharField(max_length=2, choices=Type.choices)
    title = models.CharField(max_length=100)
    details = models.TextField()
    email = models.EmailField(max_length=100, blank=True)
    resolved = models.BooleanField(default=False)
    response = models.TextField(blank=True)

    def __str__(self):
        return f'<FeedbackForm {self.id}: ({self.type}) {self.title}>'
