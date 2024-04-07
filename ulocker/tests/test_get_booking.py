from rest_framework import status
from ulocker.tests.base_test import BaseAPITestCase
from rest_framework.reverse import reverse
from ulocker.models import Locker, Booking

class GetBookingTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.booking1 = Booking.objects.create(
            user=self.user0,
            locker=self.locker1,
            applicant_name="Alice",
            matric_no="U11112222",
            phone_no="98765432",
            organization_name="NTU",
            position="Student",
            start_month="01/2025",
            duration=1
        )

    def test_get_booking_list_authenticated_user(self):
        self.client1.force_authenticate(user=self.user1)
        
        url = reverse('ulocker:user_booking_list')
        response = self.client1.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), Booking.objects.filter(user=self.user1).count())

    def test_get_booking_list_unauthenticated(self):
        url = reverse('ulocker:user_booking_list')
        response = self.client0.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_booking_list_non_empty_list(self):
        self.client0.force_authenticate(user=self.user0)

        url = reverse('ulocker:user_booking_list')
        response = self.client0.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Booking.objects.filter(user=self.user0).count())

    def test_get_booking_list_empty_list(self):
        self.client1.force_authenticate(user=self.user1)

        url = reverse('ulocker:user_booking_list')
        response = self.client1.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
