from rest_framework import status
from event.tests.base_test import BaseAPITestCase
from rest_framework.reverse import reverse
from sso.models import User
from event.models import EventAdmin
import datetime
from rest_framework.test import APIClient

class EventCreateTestCase(BaseAPITestCase):
        
    def test_create_event_success(self):
        # Try to create as event admin
        self.client1.force_authenticate(user = self.user1)
        url = reverse('event:event-create')
        resp = self.client1.post(url,
            {
                "name" : "test event",
                "allow_non_undergraduate" : False,
                "allow_exchange_student" : False,
                "start_time" : datetime.datetime(2023, 1, 22, tzinfo=datetime.timezone.utc),
                "end_time" : datetime.datetime(2023, 1, 23, tzinfo=datetime.timezone.utc),
            },
            format = 'json',
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["name"], "test event")
        self.assertEqual(resp.data["allow_non_undergraduate"], False)
        self.assertEqual(resp.data["allow_exchange_student"], False)
        self.assertEqual(resp.data["start_time"], "2023-01-22 08:00:00")
        self.assertEqual(resp.data["end_time"], "2023-01-23 08:00:00")
        self.assertEqual(EventAdmin.objects.filter(pk=resp.data["event_admin"])[0], self.eventadmin1)

    def test_create_event_fail(self):
        # Try to create as regular user
        self.client2.force_authenticate(user = self.user2)
        url = reverse('event:event-create')
        resp = self.client2.post(url,
            {
                "name" : "test event",
                "allow_non_undergraduate" : False,
                "allow_exchange_student" : False,
                "start_time" : datetime.datetime(2023, 1, 22, tzinfo=datetime.timezone.utc),
                "end_time" : datetime.datetime(2023, 1, 23, tzinfo=datetime.timezone.utc),
            },
            format = 'json',
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)