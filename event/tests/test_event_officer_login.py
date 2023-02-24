from rest_framework import status
from event.tests.base_test import BaseAPITestCase
from rest_framework.reverse import reverse
from sso.models import User
from rest_framework.test import APIClient
from event.models import EventAdmin, Event, EventOfficer
import datetime

class EventOfficerLoginTestCase(BaseAPITestCase):
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

        # Create 2 events by newuser1
        self.event1 = Event.objects.create(
            name = "test event 1",
            allow_non_undergraduate = True,
            allow_exchange_student = True,
            event_admin = self.neweventadmin1,
            start_time = datetime.datetime(2023, 1, 20, tzinfo=datetime.timezone.utc),
            end_time = datetime.datetime(2023, 1, 21, tzinfo=datetime.timezone.utc),
        )
        self.officer1 = EventOfficer.objects.create(
            name = "Bob",
            is_active = True,
            token = "ABCDEFGH",
            event = self.event1
        )

        self.event2 = Event.objects.create(
            name = "test event 2",
            allow_non_undergraduate = True,
            allow_exchange_student = True,
            event_admin = self.neweventadmin1,
            start_time = datetime.datetime(2023, 1, 20, tzinfo=datetime.timezone.utc),
            end_time = datetime.datetime(2023, 1, 21, tzinfo=datetime.timezone.utc),
        )
        self.officer2 = EventOfficer.objects.create(
            name = "Alice",
            is_active = True,
            token = "12345678",
            event = self.event2
        )

    def test_event_officer_login_success(self):
        # Try giving correct token
        self.newclient1.force_authenticate(user = self.newuser1)
        url = reverse('event:event-officer-login')
        resp = self.newclient1.post(url,
            {
                "token": self.officer1.token,
            }
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        assert(resp.data['event_id']==self.event1.pk)
        resp = self.newclient1.post(url,
            {
                "token": self.officer2.token,
            }
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        assert(resp.data['event_id']==self.event2.pk)

    def test_event_officer_login_fail(self):
        # Try giving random token
        self.newclient1.force_authenticate(user = self.newuser1)
        url = reverse('event:event-officer-login')
        resp = self.newclient1.post(url,
            {
                "token": "ABCDEFGZ",
            }
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)