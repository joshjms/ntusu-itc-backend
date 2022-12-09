from django.db import models

# Create your models here.
class SampleModel(models.Model):
    title = models.CharField(max_length=50)
    number = models.IntegerField()
