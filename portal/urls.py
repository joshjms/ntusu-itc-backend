from django.urls import path
from django.http import HttpResponse


app_name = 'portal'
urlpatterns = [
    path('', lambda _: HttpResponse("NTUSU ITC")),
]
