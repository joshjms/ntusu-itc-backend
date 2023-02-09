from rest_framework import status
from event.tests.base_test import BaseAPITestCase
from rest_framework.reverse import reverse
from sso.models import User
from event.models import Event, EventAdmin
from rest_framework.test import APIClient
import datetime

class AdminUpdateTestCase(BaseAPITestCase):

    def test_update_admin_success(self):
        # Try as superadmin
        self.client0.force_authenticate(user = self.user0)

        # Try get event admin (test1)
        url = reverse('event:admin-update',args=(self.eventadmin1.pk,))
        resp = self.client0.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        assert(resp.data['user']['username']=='test1')
        assert(resp.data['is_superadmin']==False)

        # Try put event admin (test1)
        url = reverse('event:admin-update',args=(self.eventadmin1.pk,))
        resp = self.client0.put(url,
            {
                'is_superadmin': True,
            }
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        assert(resp.data['user']['username']=='test1')
        assert(resp.data['is_superadmin']==True)

         # Try delete event admin (user1 becomes regular user)
        url = reverse('event:admin-update',args=(self.eventadmin1.pk,))
        resp = self.client0.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        
        self.client1.force_authenticate(user = self.user1)
        url = reverse('event:check-admin-status')
        resp = self.client1.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, 'regular_user')