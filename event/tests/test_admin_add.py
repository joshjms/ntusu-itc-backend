from rest_framework import status
from event.tests.base_test import BaseAPITestCase
from rest_framework.reverse import reverse
from sso.models import User
from rest_framework.test import APIClient

class AddEventAdminTestCase(BaseAPITestCase):
    @classmethod
    def setUpTestData(self):
        self.newuser1 = User.objects.create_user(
            display_name = "newtest1",
            email = "newtest1@e.ntu.edu.sg",
            username = "newtest1",
            password = "somerandompassword123$",
        )
        self.newclient1 = APIClient()

    def test_add_admins_success(self):
        # Try adding event admins as superadmin
        self.client0.force_authenticate(user = self.user0)
        url = reverse('event:add-event-admin')
        resp = self.client0.post(url,
            {
                'email': 'newtest1@e.ntu.edu.sg',
                'is_superadmin': False
            }
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        assert(resp.data['user']['username']=='newtest1')
        assert(resp.data['is_superadmin']==False)

    def test_add_admins_fail(self):
        # Try adding the event admin as non event superadmin
        self.client1.force_authenticate(user = self.user1)
        url = reverse('event:add-event-admin')
        resp = self.client1.post(url,
            {
                    'email': 'newtest1@e.ntu.edu.sg',
                    'is_superadmin': False
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try adding the event admin as non event admin
        self.client2.force_authenticate(user = self.user2)
        url = reverse('event:add-event-admin')
        resp = self.client2.post(url,
            {
                'email': 'newtest1@e.ntu.edu.sg',
                'is_superadmin': False
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)