from django.urls import path
from . import views


app_name = 'docs'
urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('docs/', views.ListView.as_view(), name='index'),
    path('docs/new/', views.CreateView.as_view(), name='create'),
    path('docs/<str:title>/', views.DetailView.as_view(), name='detail'),
    path('docs/<str:title>/edit/', views.EditView.as_view(), name='edit'),
]
