from django.urls import path
from django.http import HttpResponse
from . import views


app_name = 'modsoptimizer'
urlpatterns = [
    path('', lambda _: HttpResponse('Mods Optimizer')),
    path('scrape_course/', views.get_course_data),
    path('scrape_exam/', views.get_exam_data),
    path('course_code/', views.CourseCodeListView.as_view()),
    path('course_code/<str:course_code>/', views.CourseCodeDetailView.as_view()),
    path('optimize/', views.OptimizeView.as_view()),
]
