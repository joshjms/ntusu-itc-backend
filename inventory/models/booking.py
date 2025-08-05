from inventory.models.item import InventoryItem
from inventory.models.user import InventoryUser

from django.db import models

STATUSES = (
    ("accepted", "Accepted"),
    ("rejected", "Rejected"),
    ("processing", "Processing"),
    ("returned", "Returned"),
)

class InventoryBooking(models.Model):
    approval_status = models.CharField(max_length=10, choices=STATUSES, default="processing")
    start_date = models.DateField()
    end_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)
    quantity = models.PositiveIntegerField()
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='inventory_booking')
    user = models.ForeignKey(InventoryUser, on_delete=models.CASCADE, related_name='inventory_user')

    def __str__(self):
        return f"<(ID: {self.id}) Booking for Item, {self.item.title}, made by {self.user.user.username}, {self.approval_status}>"

    class Meta:
        verbose_name = 'Inventory Booking'
        verbose_name_plural = 'Inventory Booking'
