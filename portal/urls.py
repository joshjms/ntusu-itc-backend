from django.urls import path
from . import views


app_name = 'portal'
urlpatterns = [
    path('update/', views.UpdateNoteView.as_view()),
    path('update/<int:id>/', views.UpdateNoteView.as_view()),
]
