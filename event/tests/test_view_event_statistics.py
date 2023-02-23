from rest_framework import status
from event.tests.base_test import BaseAPITestCase
from rest_framework.reverse import reverse
from sso.models import User
from rest_framework.test import APIClient
from event.models import EventAdmin, Event, EventOfficer, MatricCheckIn
import datetime

class ViewEventStatisticsTestCase(BaseAPITestCase):
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

        self.matric1 = MatricCheckIn.objects.create(
            matric_number = "U11111111",
            event = self.event1,
            officer_name = self.officer1.name
        )
        self.matric2 = MatricCheckIn.objects.create(
            matric_number = "U22222222",
            event = self.event1,
            officer_name = self.officer1.name
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

    def test_view_event_statistics_matric_success(self):
        # Try as an event creator
        self.newclient1.force_authenticate(user = self.newuser1)
        url = reverse('event:view-event-statistics', args=(self.event1.pk,))
        resp = self.newclient1.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["matric_list"][0]["matric_number"], "U11111111")
        self.assertEqual(resp.data["matric_list"][1]["matric_number"], "U22222222")
        self.assertEqual(resp.data["check_ins"][0]["count"], 2)
        self.assertEqual(resp.data["accumulated_check_ins"][0]["count"], 2)

    def test_view_event_statistics_matric_fail(self):
        # Try as an event non creator
        self.newclient2.force_authenticate(user = self.newuser2)
        url = reverse('event:view-event-statistics', args=(self.event1.pk,))
        resp = self.newclient2.get(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)