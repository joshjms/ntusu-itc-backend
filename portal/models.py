from django.db import models


class UpdateNote(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=250)
    content = models.TextField()
    added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-added']

    def __str__(self):
        return self.title
