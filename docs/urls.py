from django.views.generic import TemplateView
from django.urls import path
from drf_yasg import openapi

app_name = 'docs'
urlpatterns = [
    path('swagger-ui/', TemplateView.as_view(
        template_name='swagger-ui.html',
        extra_context={'schema_url':'openapi-schema'}
    ), name='swagger-ui'),
]
