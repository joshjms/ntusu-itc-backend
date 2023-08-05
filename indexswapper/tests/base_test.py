from rest_framework.test import APIClient
from sso.models import User
from sso.tests.base_test import BaseAPITestCase


class IndexSwapperBaseTestCase(BaseAPITestCase):
    fixtures = ['sample_user.json', 'sample_course_index_small.json',
                'sample_swap_request_small.json']

    @classmethod
    def setUpTestData(self):
        super().setUpTestData()
        self.superuser = User.objects.get(username='superuser')
        self.user1x = User.objects.get(username='user1x')
        self.user2x = User.objects.get(username='user2x')
        self.user3x = User.objects.get(username='user3x')
        self.user4x = User.objects.get(username='user4x')
        self.user5x = User.objects.get(username='user5x')
        self.user1c = APIClient()
        self.user1c.force_authenticate(user=self.user1x)
        self.user2c = APIClient()
        self.user2c.force_authenticate(user=self.user2x)
        self.user3c = APIClient()
        self.user3c.force_authenticate(user=self.user3x)
        self.user4c = APIClient()
        self.user4c.force_authenticate(user=self.user4x)
        self.user5c = APIClient()
        self.user5c.force_authenticate(user=self.user5x)
