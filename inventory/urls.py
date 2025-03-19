from django.urls import path

from .views import (
    ItemListView,
    ItemDetailView,
    ItemLoanRequestListView,
    LoanRequestCreateView,
    LoanRequestReturnView,
    UserLoanRequestListView,
)

app_name = 'inventory'
urlpatterns = [
    path('items/', ItemListView.as_view(), name='item-list'),
    path('item/<int:item_id>', ItemDetailView.as_view(), name='item-detail'),
    path('loan-requests/', ItemLoanRequestListView.as_view(), name='loan-requests'),
    path('loan-requests/<str:username>/', UserLoanRequestListView.as_view(), name='user-loan-requests'),
    path('items/loan/', LoanRequestCreateView.as_view(), name='loan-request-create'),
    path('loan-requests/return/<int:pk>', LoanRequestReturnView.as_view(), name='loan-request-return'),
]
