from rest_framework import status
from ulocker.tests.base_test import BaseAPITestCase
from rest_framework.reverse import reverse
from ulocker.models import Locker, Booking

class AddBookingTestCase(BaseAPITestCase):

    def test_add_booking_success_single_booking(self):
        self.client1.force_authenticate(user = self.user1)
        url = reverse('ulocker:user_booking_list')

        resp = self.client1.post(url,
            {
                "locker": self.locker1.id,
                "applicant_name": "Bob",
                "matric_no": "U11112222",
                "phone_no": "98765432",
                "organization_name": "NTU",
                "position": "Student",
                "start_month": "01/2024",
                "duration": 1
            }
        )

        # check if the booking is created
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['locker'], self.locker1.id)
        self.assertEqual(resp.data['applicant_name'], 'Bob')

    def test_add_booking_success_multiple_bookings_previous_rejected(self):
        self.client0.force_authenticate(user = self.user0)
        self.client1.force_authenticate(user = self.user1)
        url = reverse('ulocker:user_booking_list')

        # create a booking with Alice
        resp = self.client0.post(url,
            {
                "locker": self.locker1.id,
                "applicant_name": "Alice",
                "matric_no": "U11112222",
                "phone_no": "98765432",
                "organization_name": "NTU",
                "position": "Student",
                "start_month": "01/2024",
                "duration": 1
            }
        )

        # change booking details and reject
        booking = Booking.objects.first()
        booking.status = Booking.AllocationStatus.REJECTED
        booking.save()

        # create a new booking with Bob
        resp = self.client1.post(url,
            {
                "locker": self.locker1.id,
                "applicant_name": "Bob",
                "matric_no": "U11112222",
                "phone_no": "98765432",
                "organization_name": "NTU",
                "position": "Student",
                "start_month": "01/2024",
                "duration": 1
            }
        )

        # check if the booking is created
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['locker'], self.locker1.id)
        self.assertEqual(resp.data['applicant_name'], 'Bob')

    def test_add_booking_success_multiple_bookings_different_lockers(self):
        self.client0.force_authenticate(user = self.user0)
        self.client1.force_authenticate(user = self.user1)
        url = reverse('ulocker:user_booking_list')

        # create a booking with Alice
        resp = self.client0.post(url,
            {
                "locker": self.locker1.id,
                "applicant_name": "Alice",
                "matric_no": "U11112222",
                "phone_no": "98765432",
                "organization_name": "NTU",
                "position": "Student",
                "start_month": "01/2024",
                "duration": 1
            }
        )

        # create a new booking with Bob
        resp = self.client1.post(url,
            {
                "locker": self.locker2.id,
                "applicant_name": "Bob",
                "matric_no": "U11112222",
                "phone_no": "98765432",
                "organization_name": "NTU",
                "position": "Student",
                "start_month": "01/2024",
                "duration": 1
            }
        )

        # check if the booking is created
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
    
    def test_add_booking_success_multiple_bookings_no_clash(self):
        self.client0.force_authenticate(user = self.user0)
        self.client1.force_authenticate(user = self.user1)
        url = reverse('ulocker:user_booking_list')

        # create a booking with Alice
        resp = self.client0.post(url,
            {
                "locker": self.locker1.id,
                "applicant_name": "Alice",
                "matric_no": "U11112222",
                "phone_no": "98765432",
                "organization_name": "NTU",
                "position": "Student",
                "start_month": "01/2024",
                "duration": 3
            }
        )

        # create a new booking with Bob
        resp = self.client1.post(url,
            {
                "locker": self.locker1.id,
                "applicant_name": "Bob",
                "matric_no": "U11112222",
                "phone_no": "98765432",
                "organization_name": "NTU",
                "position": "Student",
                "start_month": "04/2024",
                "duration": 3
            }
        )

        # check if the booking is created
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_add_booking_fail_multiple_bookings_clash(self):
        self.client0.force_authenticate(user = self.user0)
        self.client1.force_authenticate(user = self.user1)
        url = reverse('ulocker:user_booking_list')

        # create a booking with Alice
        resp = self.client0.post(url,
            {
                "locker": self.locker1.id,
                "applicant_name": "Alice",
                "matric_no": "U11112222",
                "phone_no": "98765432",
                "organization_name": "NTU",
                "position": "Student",
                "start_month": "01/2024",
                "duration": 6
            }
        )

        # create a new booking with Bob
        resp = self.client1.post(url,
            {
                "locker": self.locker1.id,
                "applicant_name": "Bob",
                "matric_no": "U11112222",
                "phone_no": "98765432",
                "organization_name": "NTU",
                "position": "Student",
                "start_month": "06/2024",
                "duration": 3
            }
        )

        # check if the booking is rejected
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_add_booking_fail_locker_id_not_found(self):
        self.client1.force_authenticate(user = self.user1)
        url = reverse('ulocker:user_booking_list')
        resp = self.client1.post(url,
            {
                "locker": 0,
                "applicant_name": "Bob",
                "matric_no": "U11112222",
                "phone_no": "98765432",
                "organization_name": "NTU",
                "position": "Student",
                "start_month": "01/2024",
                "duration": 1
            }
        )

        # check if bad request is returned
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_booking_fail_partial_filled(self):
        self.client1.force_authenticate(user = self.user1)
        url = reverse('ulocker:user_booking_list')

        resp = self.client1.post(url,
            {
                "applicant_name": "Bob",
                "matric_no": "U11112222",
                "phone_no": "98765432",
                "organization_name": "NTU",
                "position": "Student",
                "start_month": "01/2024",
                "duration": 1
            }
        )

        # check if bad request is returned
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


    def test_add_booking_fail_unauthenticated(self):
        url = reverse('ulocker:user_booking_list')
        resp = self.client0.post(url,
            {
                "locker": self.locker1.id,
                "applicant_name": "Alice",
                "matric_no": "U11112222",
                "phone_no": "98765432",
                "organization_name": "NTU",
                "position": "Student",
                "start_month": "01/2024",
                "duration": 1
            }
        )

        # check if unauthorized is returned
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)