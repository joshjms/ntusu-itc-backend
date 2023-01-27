from rest_framework import status
from event.tests.base_test import BaseAPITestCase
from rest_framework.reverse import reverse
from sso.models import User
from event.models import Event, EventAdmin
import datetime
from rest_framework.test import APIClient

class ManageEventsTestCase(BaseAPITestCase):
    @classmethod
    def setUpTestData(self):
        self.user = User.objects.create_user(
            display_name = "test user",
            email = "testuser@e.ntu.edu.sg",
            username = "testuser",
            password = "somevalidpassword123$",
        )

        self.event_admin = EventAdmin.objects.create(
            user = self.user,
            is_superadmin = True,
        )

        self.event = Event.objects.create(
            name = "test event",
            allow_non_undergraduate = True,
            allow_exchange_student = True,
            event_admin = self.event_admin,
            start_time = datetime.datetime(2023, 1, 20, tzinfo=datetime.timezone.utc),
            end_time = datetime.datetime(2023, 1, 21, tzinfo=datetime.timezone.utc),
        )

        self.client = APIClient()

    def test_get_event_success(self):
        # Try viewing all the events as event superadmin
        self.client0.force_authenticate(user = self.user0)
        url = reverse('event:all_events')
        resp = self.client0.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data[0]["name"], "test event")
        self.assertEqual(resp.data[0]["allow_non_undergraduate"], True)
        self.assertEqual(resp.data[0]["allow_exchange_student"], True)
        self.assertEqual(resp.data[0]["event_admin"], self.event_admin)
        self.assertEqual(resp.data[0]["start_time"], "2023-01-20T08:00:00+08:00")
        self.assertEqual(resp.data[0]["end_time"], "2023-01-21T08:00:00+08:00")