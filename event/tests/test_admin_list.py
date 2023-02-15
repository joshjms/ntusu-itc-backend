from rest_framework import status
from event.tests.base_test import BaseAPITestCase
from rest_framework.reverse import reverse

class AdminListTestCase(BaseAPITestCase):
    
    def test_get_admins_success(self):
        # Try viewing all the event admin as superadmin
        self.client0.force_authenticate(user = self.user0)
        url = reverse('event:admin-list')
        resp = self.client0.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        assert(resp.data[0]['user']['username']=='test0')
        assert(resp.data[0]['is_superadmin']==True)
        assert(resp.data[1]['user']['username']=='test1')
        assert(resp.data[1]['is_superadmin']==False)

    def test_get_admins_fail(self):
        # Try viewing all the event admin as non event superadmin
        self.client1.force_authenticate(user = self.user1)
        url = reverse('event:admin-list')
        resp = self.client1.get(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try viewing all the event admin as non event admin
        self.client2.force_authenticate(user = self.user2)
        url = reverse('event:admin-list')
        resp = self.client2.get(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)