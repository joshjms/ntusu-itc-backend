from rest_framework import status
from event.tests.base_test import BaseAPITestCase
from rest_framework.reverse import reverse
from sso.models import User
from rest_framework.test import APIClient
from event.models import EventAdmin, Event, EventOfficer
import datetime

class EditOfficerTestCase(BaseAPITestCase):
    @classmethod
    def setUpTestData(self):
        self.newuser1 = User.objects.create_user(
            display_name = "newtest1",
            email = "newtest1@e.ntu.edu.sg",
            username = "newtest1",
            password = "somerandompassword123$",
        )
        self.neweventadmin1 = EventAdmin.objects.create(
            user = self.newuser1,
            is_superadmin = False,
        )
        self.newclient1 = APIClient()

        # Create an event by newuser1
        self.event1 = Event.objects.create(
            name = "test event 1",
            allow_non_undergraduate = True,
            allow_exchange_student = True,
            event_admin = self.neweventadmin1,
            start_time = datetime.datetime(2023, 1, 20, tzinfo=datetime.timezone.utc),
            end_time = datetime.datetime(2023, 1, 21, tzinfo=datetime.timezone.utc),
        )

        # Create an officer for that event
        self.officer1 = EventOfficer.objects.create(
            name = "Bob",
            is_active = True,
            token = "ABCDEFGH",
            event = self.event1
        )

        # Add a "foreign" event admin
        self.newuser2 = User.objects.create_user(
            display_name = "newtest2",
            email = "newtest2@e.ntu.edu.sg",
            username = "newtest2",
            password = "somerandompassword123$",
        )
        self.neweventadmin2 = EventAdmin.objects.create(
            user = self.newuser2,
            is_superadmin = False,
        )
        self.newclient2 = APIClient()

    def test_edit_officer_success(self):
        # Try adding event admins as event creator
        self.newclient1.force_authenticate(user = self.newuser1)
        url = reverse('event:edit-officer', args=(self.officer1.token,))

        # test get
        resp = self.newclient1.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        assert(resp.data['name']=='Bob')
        assert(resp.data['is_active']==True)

        # test put
        resp = self.newclient1.put(url,
            {
                "name": "Alice",
                "is_active": False
            }
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        assert(resp.data['name']=='Alice')
        assert(resp.data['is_active']==False)

        # test delete
        resp = self.newclient1.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_edit_officer_fail(self):
        # Try adding event admins as non event creator
        self.newclient2.force_authenticate(user = self.newuser2)
        url = reverse('event:edit-officer',args=(self.officer1.token,))
        resp = self.newclient2.put(url,
            {
                "name": "Alice",
                "is_active": False
            }
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)