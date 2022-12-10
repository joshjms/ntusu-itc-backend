from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator


class User(AbstractUser):
    display_name = models.CharField(max_length=40)
    email = models.EmailField(unique=True)
    custom_token = models.CharField(max_length=20, blank=True)
    token_expiry_date = models.DateTimeField(blank=True, null=True)
    description = models.TextField(
        validators=[MaxLengthValidator(100)],
        blank=True, default=''
    )
    
    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return f'<User ID {self.id}: {self.username}>'
