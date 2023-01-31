from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from ufacility.models import UFacilityUser, Booking2, Venue
from ufacility.tests.base_test import BaseAPITestCase
from sso.models import User
import datetime as dt


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
            hongen_name = "hg",
            hongen_phone_number = "87654321",
        )

        self.venue = Venue.objects.create(
            name = "test venue",
            security_email = "security@e.ntu.edu.sg",
        )

        self.booking = Booking2.objects.create(
            user = self.ufacilityuser,
            venue = self.venue,
            date = dt.date(2023, 1, 29),
            start_time = dt.time(hour=15),
            end_time = dt.time(hour=19),
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
        self.assertEqual(resp.data[0]["date"], "2023-01-29")
        self.assertEqual(resp.data[0]["start_time"], "15:00:00")
        self.assertEqual(resp.data[0]["end_time"], "19:00:00")
        self.assertEqual(resp.data[0]["purpose"], "test purpose")
        self.assertEqual(resp.data[0]["status"], "pending")
        self.assertEqual(resp.data[0]["pax"], 10)

        # Test request as the ufacility user itself
        self.client.force_authenticate(user = self.user)
        self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data[0]["user"], self.ufacilityuser.id)
        self.assertEqual(resp.data[0]["venue"], self.venue.id)
        self.assertEqual(resp.data[0]["date"], "2023-01-29")
        self.assertEqual(resp.data[0]["start_time"], "15:00:00")
        self.assertEqual(resp.data[0]["end_time"], "19:00:00")
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
