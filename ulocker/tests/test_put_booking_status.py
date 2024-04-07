from rest_framework import status
from rest_framework.reverse import reverse
from ulocker.models import Booking
from ulocker.tests.base_test import BaseAPITestCase

class ChangeBookingStatusViewTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.booking1 = Booking.objects.create(
            user=self.user1,
            locker=self.locker1,
            applicant_name="Admin",
            matric_no="U11112222",
            phone_no="98765432",
            organization_name="NTU",
            position="Student",
            start_month="01/2025",
            duration=1
        )

    def test_put_status_success(self):
        self.client1.force_authenticate(user=self.user1)
        url = reverse('ulocker:change_booking_status')
        response = self.client1.put(url, data={'booking_id': self.booking1.id, 'status': 'withdrawn'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_status_fail_no_booking_id_found(self):
        self.client1.force_authenticate(user=self.user1)
        url = reverse('ulocker:change_booking_status')
        response = self.client1.put(url, data={'booking_id': 9999, 'status': 'withdrawn'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_status_fail_invalid_status(self):
        self.client1.force_authenticate(user=self.user1)
        url = reverse('ulocker:change_booking_status')
        response = self.client1.put(url, data={'booking_id': self.booking1.id, 'status': 'random'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_status_fail_non_authenticated_non_admin(self):
        url = reverse('ulocker:change_booking_status')
        response = self.client0.put(url, data={'booking_id': self.booking1.id, 'status': 'withdrawn'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_status_fail_authenticated_non_admin(self):
        self.client0.force_authenticate(user=self.user0)
        url = reverse('ulocker:change_booking_status')
        response = self.client0.put(url, data={'booking_id': self.booking1.id, 'status': 'withdrawn'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_status_fail_non_authenticated_admin(self):
        url = reverse('ulocker:change_booking_status')
        response = self.client1.put(url, data={'booking_id': self.booking1.id, 'status': 'withdrawn'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

