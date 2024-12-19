from django.db import models
from sso.models import User
from django.utils.crypto import get_random_string


STATUSES = (
    ("accepted", "Accepted"),
    ("rejected", "Rejected"),
    ("processing", "Processing"),
)


def get_item_path(instance, filename):
    unique_identifier = get_random_string(12)
    return f'inventory/item_files/{unique_identifier}_{filename}'


class InventoryUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f'<Inventory User: {self.user.username}>'

    class Meta:
        verbose_name = 'Inventory User'
        verbose_name_plural = 'Inventory Users'


class InventoryLender(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organisation = models.CharField(max_length=30)
    
    def __str__(self):
        return f'<Inventory Lender: {self.user.username} ({self.organisation})>'

    class Meta:
        verbose_name = 'Inventory Lender'
        verbose_name_plural = 'Inventory Lenders'


class Item(models.Model):
    title = models.CharField(max_length=50, unique=True)
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


class ItemLoanRequest(models.Model):
    approval_status = models.CharField(max_length=10, choices=STATUSES, default="Processing")
    start_date = models.DateField()
    end_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)
    quantity = models.PositiveIntegerField()
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='item_loan_requests')
    user = models.ForeignKey(InventoryUser, on_delete=models.CASCADE, related_name='user_loan_requests')

    def __str__(self):
        return f"<(ID: {self.id}) Loan request for Item, {self.item.title}, made by {self.user.user.username}, {self.approval_status}>"
