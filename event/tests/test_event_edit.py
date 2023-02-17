from rest_framework import status
from event.tests.base_test import BaseAPITestCase
from rest_framework.reverse import reverse
from sso.models import User
from event.models import Event, EventAdmin
import datetime
from rest_framework.test import APIClient

class EventEditTestCase(BaseAPITestCase):
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

        # Create 1 events
        self.event1 = Event.objects.create(
            name = "test event 1",
            allow_non_undergraduate = True,
            allow_exchange_student = True,
            event_admin = self.neweventadmin1,
            start_time = datetime.datetime(2023, 1, 20, tzinfo=datetime.timezone.utc),
            end_time = datetime.datetime(2023, 1, 21, tzinfo=datetime.timezone.utc),
        )
        

    def test_edit_event_success(self):
        # Try creator edit the event

        # Try get
        self.newclient1.force_authenticate(user = self.newuser1)
        url = reverse('event:event-edit', args=(self.event1.id,))
        resp = self.newclient1.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Try put
        resp = self.newclient1.put(url,
            {
                "name" : "test event",
                "allow_non_undergraduate" : False,
                "allow_exchange_student" : False,
                "start_time" : datetime.datetime(2023, 1, 22, tzinfo=datetime.timezone.utc),
                "end_time" : datetime.datetime(2023, 1, 23, tzinfo=datetime.timezone.utc),
            }
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["name"], "test event")
        self.assertEqual(resp.data["allow_non_undergraduate"], False)
        self.assertEqual(resp.data["allow_exchange_student"], False)
        self.assertEqual(resp.data["start_time"], "2023-01-22 08:00:00")
        self.assertEqual(resp.data["end_time"], "2023-01-23 08:00:00")
        self.assertEqual(EventAdmin.objects.filter(pk=resp.data["event_admin"])[0], self.neweventadmin1)

        # Try delete
        resp = self.newclient1.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        url = reverse('event:event-list')
        resp = self.newclient1.get(url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 0)

    def test_edit_event_fail(self):
        # Try non creator edit the event

        # Try get
        self.newclient2.force_authenticate(user = self.newuser2)
        url = reverse('event:event-edit', args=(self.event1.id,))
        resp = self.newclient2.get(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # Try put
        resp = self.newclient2.put(url,
            {
                "name" : "test event",
                "allow_non_undergraduate" : False,
                "allow_exchange_student" : False,
                "start_time" : datetime.datetime(2023, 1, 22, tzinfo=datetime.timezone.utc),
                "end_time" : datetime.datetime(2023, 1, 23, tzinfo=datetime.timezone.utc),
            }
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # Try delete
        resp = self.newclient2.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)