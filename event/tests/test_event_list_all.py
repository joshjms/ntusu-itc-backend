from rest_framework import status
from event.tests.base_test import BaseAPITestCase
from rest_framework.reverse import reverse
from sso.models import User
from event.models import Event, EventAdmin
import datetime
from rest_framework.test import APIClient

class EventListAllTestCase(BaseAPITestCase):
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
            is_superadmin = True,
        )

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

        # Create 2 events
        self.event1 = Event.objects.create(
            name = "test event 1",
            allow_non_undergraduate = True,
            allow_exchange_student = True,
            event_admin = self.neweventadmin1,
            start_time = datetime.datetime(2023, 1, 20, tzinfo=datetime.timezone.utc),
            end_time = datetime.datetime(2023, 1, 21, tzinfo=datetime.timezone.utc),
        )
        self.event2 = Event.objects.create(
            name = "test event 2",
            allow_non_undergraduate = False,
            allow_exchange_student = False,
            event_admin = self.neweventadmin2,
            start_time = datetime.datetime(2023, 1, 22, tzinfo=datetime.timezone.utc),
            end_time = datetime.datetime(2023, 1, 23, tzinfo=datetime.timezone.utc),
        )

        self.client = APIClient()

    def test_get_all_events_success(self):
        # Try viewing all the events as event superadmin
        self.client0.force_authenticate(user = self.user0)
        url = reverse('event:event-list-all')
        resp = self.client0.get(url)
        
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data[0]["name"], "test event 1")
        self.assertEqual(resp.data[0]["allow_non_undergraduate"], True)
        self.assertEqual(resp.data[0]["allow_exchange_student"], True)
        self.assertEqual(resp.data[0]["start_time"], "2023-01-20 08:00:00")
        self.assertEqual(resp.data[0]["end_time"], "2023-01-21 08:00:00")
        self.assertEqual(EventAdmin.objects.filter(pk=resp.data[0]["event_admin"])[0], self.neweventadmin1)
        self.assertEqual(resp.data[1]["name"], "test event 2")
        self.assertEqual(resp.data[1]["allow_non_undergraduate"], False)
        self.assertEqual(resp.data[1]["allow_exchange_student"], False)
        self.assertEqual(resp.data[1]["start_time"], "2023-01-22 08:00:00")
        self.assertEqual(resp.data[1]["end_time"], "2023-01-23 08:00:00")
        self.assertEqual(EventAdmin.objects.filter(pk=resp.data[1]["event_admin"])[0], self.neweventadmin2)

    def test_get_all_events_fail(self):
        # Try viewing all the events as event admin
        self.client1.force_authenticate(user = self.user1)
        url = reverse('event:event-list-all')
        resp = self.client1.get(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # Try viewing all the events as a non event admin
        self.client2.force_authenticate(user = self.user2)
        url = reverse('event:event-list-all')
        resp = self.client2.get(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)