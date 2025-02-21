from django.contrib import admin

from inventory.models import (
    InventoryUser, 
    InventoryLender, 
    Item, 
    ItemLoanRequest,
)

admin.site.register(InventoryUser)
admin.site.register(InventoryLender)
admin.site.register(Item)
admin.site.register(ItemLoanRequest)
