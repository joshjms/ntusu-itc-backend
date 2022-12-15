from django.urls import path
from django.http import HttpResponse
from . import views


app_name = 'portal'
urlpatterns = [
    path('', lambda _: HttpResponse("Portal")),
    path('update/', views.UpdateNoteView.as_view(), name='update'),
    path('update/<int:id>/', views.UpdateNoteDetailView.as_view(), name='update_detail'),
    path('feedback/', views.FeedbackView.as_view(), name='feedback'),
    path('feedback/<int:id>/', views.FeedbackDetailView.as_view(), name='feedback_detail'),
]
