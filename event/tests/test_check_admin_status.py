from rest_framework import status
from event.tests.base_test import BaseAPITestCase
from rest_framework.reverse import reverse
from sso.models import User
from event.models import Event, EventAdmin
import datetime
from rest_framework.test import APIClient

class CheckAdminStatusTestCase(BaseAPITestCase):

    def test_get_events_success(self):
        # Try login as superadmin 
        self.client0.force_authenticate(user = self.user0)
        url = reverse('event:check-admin-status')
        resp = self.client0.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, 'event_superadmin')

        # Try login as admin 
        self.client1.force_authenticate(user = self.user1)
        url = reverse('event:check-admin-status')
        resp = self.client1.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, 'event_admin')

        # Try login as regular user 
        self.client2.force_authenticate(user = self.user2)
        url = reverse('event:check-admin-status')
        resp = self.client2.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, 'regular_user')