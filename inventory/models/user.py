from sso.models import User

from django.db import models

class InventoryUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f'<Inventory User: {self.user.username}>'

    class Meta:
        verbose_name = 'Inventory User'
        verbose_name_plural = 'Inventory Users'
