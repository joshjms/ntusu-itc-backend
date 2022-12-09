from django.urls import path
from django.http import HttpResponse, JsonResponse
from sso.utils import send_email


app_name = 'portal'
urlpatterns = [
    path('', lambda _: HttpResponse("NTUSU ITC")),
    path('email_test', lambda _: JsonResponse(send_email(
        'do-not-reply',
        'mich0107@e.ntu.edu.sg',
        'TESTING',
        'some content...'
    )))
]
