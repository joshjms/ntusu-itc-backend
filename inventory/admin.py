from django.contrib import admin
from django.db.models import Count, Q, F
from inventory.models import InventoryUser, InventoryLender, InventoryItem, InventoryBooking


class AvailabilityFilter(admin.SimpleListFilter):
    """ Custom list filter to filter items based on availability (on loan or not)"""

    title = 'availability'
    parameter_name = 'availability'

    def lookups(self, request, model_admin):
        return (
            ('available', 'Available'),
            ('not_available', 'Not Available')
        )

    def queryset(self, request, queryset):
        # Annotate queryset with on_loan count
        queryset = queryset.annotate(
            on_loan=Count(
                'item_bookings', 
                filter=Q(item_bookings__approval_status='accepted') & \
                    Q(item_bookings__return_date__isnull=True)
            )
        )
        if self.value() == 'available':
            return queryset.filter(on_loan__lt=F('quantity'))
        elif self.value() == 'not_available':
            return queryset.filter(on_loan__gte=F('quantity'))
        return queryset


@admin.register(InventoryUser)
class InventoryUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'user_email']

    def user_email(self, obj):
        return obj.user.email


@admin.register(InventoryLender)
class InventoryLenderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'organisation_name', 'user_email']
    list_filter = ['organisation_name']

    def user_email(self, obj):
        return obj.user.email


@admin.register(InventoryItem)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'quantity', 'lender', 'booking_count', 'is_available']
    list_filter = ['category', AvailabilityFilter]
    search_fields = ['title']

    def get_queryset(self, request):
        # Annotate queryset with booking_count and on_loan count
        return super().get_queryset(request).annotate(
            booking_count=Count('item_bookings'),
            on_loan=Count(
                'item_bookings', 
                filter=Q(item_bookings__approval_status='accepted') & \
                    Q(item_bookings__return_date__isnull=True)
            )
        )

    def lender(self, obj):
        return obj.user

    @admin.display(description='Bookings')
    def booking_count(self, obj):
        return obj.booking_count

    @admin.display(boolean=True)
    def is_available(self, obj):
        # Check if the number currently on loan is less than the total quantity
        return obj.on_loan < obj.quantity


@admin.register(InventoryBooking)
class ItemLoanRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'approval_status', 'start_date', 'end_date', 'return_date', 'quantity', 'item', 'user']
    list_filter = ['approval_status', 'start_date', 'end_date', 'return_date']
    search_fields = ['item__title']
