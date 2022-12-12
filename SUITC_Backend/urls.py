"""SUITC_Backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from drf_yasg import openapi
from drf_yasg.views import get_schema_view


schema_view = get_schema_view(
    openapi.Info(
        title='NTUSU ITC BACKEND API',
        default_version='1.0.0',
        description='Auto generated API documentation :)',
    ), public=True
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger'), name='swagger'),
    path('summernote/', include('django_summernote.urls')),

    path('', include('docs.urls')),
    path('portal/', include('portal.urls')),
    path('sso/', include('sso.urls')),
    path('ufacility/', include('ufacility.urls')),
    path('inventory/', include('inventory.urls')),
    path('event/', include('event.urls')),
    path('starswar/', include('starswar.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
