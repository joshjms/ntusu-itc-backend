from inventory.models.lender import InventoryLender
from inventory.utils import get_item_path

from django.db import models

class InventoryItem(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=30)
    attachment = models.FileField(
        upload_to=get_item_path, 
        blank=True, null=True
    )
    quantity = models.PositiveIntegerField()
    user = models.ForeignKey(InventoryLender, on_delete=models.CASCADE, related_name='lender_items')

    def __str__(self):
        return f"<(ID: {self.id}) {self.title}>"

    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Items'
