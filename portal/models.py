from django.db import models


class UpdateNote(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=250)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title
