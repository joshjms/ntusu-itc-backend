from django.urls import path
from django.http import HttpResponse
from . import views


app_name = 'portal'
urlpatterns = [
    path('', lambda _: HttpResponse("Portal")),
    path('update/', views.UpdateNoteView.as_view(), name='update'),
    path('update/<int:id>/', views.UpdateNoteDetailView.as_view(), name='update_detail'),
]
