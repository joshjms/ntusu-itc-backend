from rest_framework import status
from event.tests.base_test import BaseAPITestCase
from rest_framework.reverse import reverse
from sso.models import User
from event.models import Event, EventAdmin
import datetime
from rest_framework.test import APIClient

class AdminGetUserListTestCase(BaseAPITestCase):        

    def test_get_events_success(self):
        # Try viewing all the user email as event superadmin
        self.client0.force_authenticate(user = self.user0)
        url = reverse('event:admin-get-user-list')
        resp = self.client0.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Currently user2 is not registered as event admin
        self.assertEqual(resp.data[0]["email"], "test2@e.ntu.edu.sg")
        self.assertEqual(resp.data[0]["display_name"], "test2")
        self.assertEqual(resp.data[0]["username"], "test2")

    def test_get_events_fail(self):
        # Try viewing all the user email as event admin
        self.client1.force_authenticate(user = self.user1)
        url = reverse('event:admin-get-user-list')
        resp = self.client1.get(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # Try viewing all the user email as regular user
        self.client2.force_authenticate(user = self.user2)
        url = reverse('event:admin-get-user-list')
        resp = self.client2.get(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)