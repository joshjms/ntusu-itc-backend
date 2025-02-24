from django.urls import path

from .views import (
    ItemListView,
    ItemDetailView,
    ItemLoanRequestListView,
    LoanRequestCreateView,
    LoanRequestReturnView,
)

app_name = 'inventory'
urlpatterns = [
    path('items/', ItemListView.as_view(), name='item-list'),
    path('item/<int:item_id>', ItemDetailView.as_view(), name='item-detail'),
    path('loan-requests/', ItemLoanRequestListView.as_view(), name='loan-requests'),
    path('items/loan/', LoanRequestCreateView.as_view(), name='loan-request-create'),
    path('items/loan/return/<int:pk>', LoanRequestReturnView.as_view(), name='loan-request-return'),
]
