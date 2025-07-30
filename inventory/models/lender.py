from sso.models import User

from django.db import models

class InventoryLender(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organisation_name = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return f'<Inventory Lender: {self.user.username} ({self.organisation_name})>'

    class Meta:
        verbose_name = 'Inventory Lender'
        verbose_name_plural = 'Inventory Lenders'
