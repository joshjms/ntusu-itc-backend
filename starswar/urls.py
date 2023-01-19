from rest_framework import routers
from starswar.views import (
    CourseIndexViewSet,
    SwapRequestViewSet
)


app_name = 'starswar'
router = routers.DefaultRouter()
router.register('modules', CourseIndexViewSet, basename='modules')
router.register('swaprequest', SwapRequestViewSet, basename='swaprequest')

urlpatterns = [] + router.urls
