from rest_framework import routers
from starswar.views import (
    CourseIndexViewSet,
    SwapRequestViewSet
)


app_name = 'starswar'
router = routers.DefaultRouter()
router.register('modules', CourseIndexViewSet, basename='modules')

urlpatterns = [] + router.urls
# print(urlpatterns) DEBUG TODO
