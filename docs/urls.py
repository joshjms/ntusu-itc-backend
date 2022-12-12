from django.urls import path
from django.shortcuts import render


app_name = 'docs'
urlpatterns = [
    path('', lambda req: render(req, 'index.html'), name='index'),
    path('docs/', lambda req: render(req, 'docs.html'), name='main'),
]
