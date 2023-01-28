from rest_framework import status
from ufacility.tests.base_test import BaseAPITestCase
from rest_framework.reverse import reverse
from sso.models import User
from ufacility.models import UFacilityUser, Booking2, Venue
import datetime
from rest_framework.test import APIClient


class UfacilityUserBookingsTestCase(BaseAPITestCase):
    @classmethod
    def setUpTestData(self):
        self.user = User.objects.create_user(
            display_name = "test user",
            email = "testuser@e.ntu.edu.sg",
            username = "testuser",
            password = "somevalidpassword123$",
        )

        self.ufacilityuser = UFacilityUser.objects.create(
            user = self.user,
            is_admin = False,
            cca = "su",
            role = "member",
        )

        self.venue = Venue.objects.create(
            name = "test venue",
            security_email = "security@e.ntu.edu.sg",
        )

        self.booking = Booking2.objects.create(
            user = self.ufacilityuser,
            venue = self.venue,
            start_time = datetime.datetime(2023, 1, 20, tzinfo=datetime.timezone.utc),
            end_time = datetime.datetime(2023, 1, 21, tzinfo=datetime.timezone.utc),
            purpose = "test purpose",
            status = "pending",
            pax = 10,
        )

        self.client = APIClient()

    def test_get_user_bookings_success(self):
        # Test request as admin
        self.client0.force_authenticate(user = self.user0)
        url = reverse('ufacility:user-bookings', kwargs={"user_id": self.ufacilityuser.id})
        resp = self.client0.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data[0]["user"], self.ufacilityuser.id)
        self.assertEqual(resp.data[0]["venue"], self.venue.id)
        self.assertEqual(resp.data[0]["start_time"], "2023-01-20T08:00:00+08:00")
        self.assertEqual(resp.data[0]["end_time"], "2023-01-21T08:00:00+08:00")
        self.assertEqual(resp.data[0]["purpose"], "test purpose")
        self.assertEqual(resp.data[0]["status"], "pending")
        self.assertEqual(resp.data[0]["pax"], 10)

        # Test request as the ufacility user itself
        self.client.force_authenticate(user = self.user)
        self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data[0]["user"], self.ufacilityuser.id)
        self.assertEqual(resp.data[0]["venue"], self.venue.id)
        self.assertEqual(resp.data[0]["start_time"], "2023-01-20T08:00:00+08:00")
        self.assertEqual(resp.data[0]["end_time"], "2023-01-21T08:00:00+08:00")
        self.assertEqual(resp.data[0]["purpose"], "test purpose")
        self.assertEqual(resp.data[0]["status"], "pending")
        self.assertEqual(resp.data[0]["pax"], 10)

    def test_get_user_bookings_fail_unauthorized(self):
        self.client2.force_authenticate(user = self.user2)
        url = reverse('ufacility:user-bookings', kwargs={"user_id": self.ufacilityuser.id})
        resp = self.client2.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_bookings_fail_forbidden(self):
        self.client1.force_authenticate(user = self.user1)
        url = reverse('ufacility:user-bookings', kwargs={"user_id": self.ufacilityuser.id})
        resp = self.client1.get(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user_bookings_fail_not_found(self):
        self.client0.force_authenticate(user = self.user0)
        url = reverse('ufacility:user-bookings', kwargs={"user_id": 999})
        resp = self.client0.get(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

