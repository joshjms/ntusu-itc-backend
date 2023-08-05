from django.urls import path
from rest_framework import routers
from indexswapper.utils.locking_test import locking_test_api
from indexswapper.views import (
    PopulateDatabaseView,
    CourseIndexViewSet,
    SwapRequestViewSet,
)


app_name = 'indexswapper'
router = routers.DefaultRouter()
router.register('courseindex', CourseIndexViewSet, basename='courseindex')
router.register('swaprequest', SwapRequestViewSet, basename='swaprequest')

urlpatterns = [
    path('populate_db/',
         PopulateDatabaseView.as_view(), name='populate_db'),
    # TODO - test this using mysql, not using sqlite3!
    path('locking_test/', locking_test_api, name='test'),
] + router.urls
