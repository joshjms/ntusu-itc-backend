from rest_framework import status
from event.tests.base_test import BaseAPITestCase
from rest_framework.reverse import reverse
from sso.models import User
from rest_framework.test import APIClient
from event.models import EventAdmin, Event
import datetime

class AddEventOfficerTestCase(BaseAPITestCase):
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

    def test_add_officer_success(self):
        # Try adding event admins as event creator
        self.newclient1.force_authenticate(user = self.newuser1)
        url = reverse('event:add-event-officer',args=(self.event1.pk,))
        resp = self.newclient1.post(url,
            {
                "name": "Bob",
                "is_active": True
            }
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['name'], 'Bob')
        self.assertEqual(resp.data['is_active'], True)
        self.assertEqual(resp.data['event'], self.event1.id)

    def test_add_officer_fail(self):
        # Try adding event admins as non event creator
        self.newclient2.force_authenticate(user = self.newuser2)
        url = reverse('event:add-event-officer',args=(self.event1.pk,))
        resp = self.newclient2.post(url,
            {
                "name": "Bob",
                "is_active": True
            }
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)