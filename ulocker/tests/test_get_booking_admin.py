from rest_framework import status
from rest_framework.reverse import reverse
from ulocker.models import Booking
from ulocker.tests.base_test import BaseAPITestCase

class AdminBookingListViewTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.booking1 = Booking.objects.create(
            user=self.user0,
            locker=self.locker1,
            applicant_name="Mario123",
            matric_no="U11112222",
            phone_no="98765432",
            organization_name="NTU",
            position="Student",
            start_month="01/2025",
            duration=1
        )

        self.booking2 = Booking.objects.create(
            user=self.user1,
            locker=self.locker2,
            applicant_name="Admin",
            matric_no="U11112222",
            phone_no="98765432",
            organization_name="NTU",
            position="Student",
            start_month="6/2024",
            duration=1
        )

    def test_get_booking_admin_authenticated_success(self):
        self.client1.force_authenticate(user=self.user1)

        url = reverse('ulocker:admin_booking_list')
        response = self.client1.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 2)

    def test_search_by_applicant_name_success(self):
        self.client1.force_authenticate(user=self.user1)

        url = reverse('ulocker:admin_booking_list')
        response = self.client1.get(url, {'search': 'Mario'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_search_by_applicant_name_empty(self):
        self.client1.force_authenticate(user=self.user1)

        url = reverse('ulocker:admin_booking_list')
        response = self.client1.get(url, {'search': 'Marioasdfasdfasdf'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_order_by_creation_date(self):
        self.client1.force_authenticate(user=self.user1)

        url = reverse('ulocker:admin_booking_list')
        response = self.client1.get(url, {'ordering': 'creation_date'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  

    def test_order_by_start_month(self):
        self.client1.force_authenticate(user=self.user1)

        url = reverse('ulocker:admin_booking_list')
        response = self.client1.get(url, {'ordering': 'start_month'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_booking_admin_unauthenticated_fail(self):
        url = reverse('ulocker:admin_booking_list')
        response = self.client1.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_booking_nonadmin_authenticated_fail(self):
        self.client0.force_authenticate(user=self.user0)

        url = reverse('ulocker:admin_booking_list')
        response = self.client0.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_booking_nonadmin_authenticated_fail(self):
        url = reverse('ulocker:admin_booking_list')
        response = self.client0.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        


    