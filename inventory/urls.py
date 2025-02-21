from django.urls import path

from .views import (
    ItemListView,
    ItemLoanRequestListView,
)

app_name = 'inventory'
urlpatterns = [
    path('items/', ItemListView.as_view(), name='item-list'),
]
