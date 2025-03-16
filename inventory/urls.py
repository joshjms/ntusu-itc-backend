from django.urls import path
from .views import ItemListCreateView, ItemDetailView

app_name = 'inventory'

urlpatterns = [
    path('items/', ItemListCreateView.as_view(), name='item-list-create'),
    path('items/<int:pk>/', ItemDetailView.as_view(), name='item-detail'),
]
