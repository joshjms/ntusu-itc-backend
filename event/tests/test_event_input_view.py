from rest_framework import status
from event.tests.base_test import BaseAPITestCase
from rest_framework.reverse import reverse
from sso.models import User
from rest_framework.test import APIClient
from event.models import EventAdmin, Event, EventOfficer
import datetime

class EventInputViewTestCase(BaseAPITestCase):
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

        # event 1 allow N and P prefixes of matric number
        self.event1 = Event.objects.create(
            name = "test event 1",
            allow_non_undergraduate = True,
            allow_exchange_student = True,
            event_admin = self.neweventadmin1,
            start_time = datetime.datetime(2023, 1, 20, tzinfo=datetime.timezone.utc),
            end_time = datetime.datetime(2050, 1, 21, tzinfo=datetime.timezone.utc),
        )
        self.officer1 = EventOfficer.objects.create(
            name = "Bob",
            is_active = True,
            token = "ABCDEFGH",
            event = self.event1
        )

        # event 2 does not allow N and P prefixes of matric number
        self.event2 = Event.objects.create(
            name = "test event 2",
            allow_non_undergraduate = False,
            allow_exchange_student = False,
            event_admin = self.neweventadmin1,
            start_time = datetime.datetime(2023, 1, 20, tzinfo=datetime.timezone.utc),
            end_time = datetime.datetime(2050, 1, 21, tzinfo=datetime.timezone.utc),
        )
        self.officer2 = EventOfficer.objects.create(
            name = "Alice",
            is_active = True,
            token = "12345678",
            event = self.event2
        )
        self.officer3 = EventOfficer.objects.create(
            name = "Charlie",
            is_active = True,
            token = "QWERTY12",
            event = self.event2
        )
        self.officer4 = EventOfficer.objects.create(
            name = "Don",
            is_active = False,
            token = "ZXCVBNMM",
            event = self.event2
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


    def test_event_input_view_success(self):
        self.newclient1.force_authenticate(user = self.newuser1)
        url = reverse('event:event-input-view', args=(self.event1.pk,))
        
        # Try as undergraduate
        resp = self.newclient1.post(url,
            {
                "token": self.officer1.token,
                "matric_number": "U2123128C",
            }
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['detail'], "Successfully checked in")

        # Try as postgraduate
        resp = self.newclient1.post(url,
            {
                "token": self.officer1.token,
                "matric_number": "G2123128C",
            }
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['detail'], "Successfully checked in")

        # Try as exchange student
        resp = self.newclient1.post(url,
            {
                "token": self.officer1.token,
                "matric_number": "N2123128C",
            }
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['detail'], "Successfully checked in")

    def test_event_input_view_fail(self):
        self.newclient2.force_authenticate(user = self.newuser2)
        url = reverse('event:event-input-view', args=(self.event2.pk,))

        # Try as postgraduate
        resp = self.newclient2.post(url,
            {
                "token": self.officer2.token,
                "matric_number": "G2123128C",
            }
        )
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(resp.data['detail'], "This event is only open to undergraduate students")

        # Try as exchange student
        resp = self.newclient2.post(url,
            {
                "token": self.officer2.token,
                "matric_number": "N2123128C",
            }
        )
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(resp.data['detail'], "Exchange students are not allowed for this event")

        # Try login multiple times with different officers
        resp = self.newclient2.post(url,
            {
                "token": self.officer2.token,
                "matric_number": "U2123128C",
            }
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        resp = self.newclient2.post(url,
            {
                "token": self.officer3.token,
                "matric_number": "U2123128C",
            }
        )
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        expected_error_msg = f"Matric card U2123128C already checked in at counter {self.officer2.name}"
        self.assertEqual(resp.data['detail'], expected_error_msg)

        # Try login to unactive officer
        resp = self.newclient2.post(url,
            {
                "token": self.officer4.token,
                "matric_number": "U1232312X",
            }
        )
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        expected_error_msg = "You are not currently assigned to any active counter"
        self.assertEqual(resp.data['detail'], expected_error_msg)