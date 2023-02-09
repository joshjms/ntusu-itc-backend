from rest_framework import status
from rest_framework.reverse import reverse
import datetime as dt
from json import loads
from ufacility.models import Booking2, Venue
from ufacility.tests.base_test import BaseAPITestCase


class UfacilityVerificationsTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.venue1 = Venue.objects.create(
            name='minerva',
            security_email='security@mail.com',
        )
        self.venue2 = Venue.objects.create(
            name='athena',
            security_email='other_security@mail.com',
        )
        self.booking1 = Booking2.objects.create(
            user=self.ufacilityuser1,
            venue=self.venue1,
            date=dt.date(2050, 1, 20),
            start_time=dt.time(hour=13),
            end_time=dt.time(hour=16),
            purpose='dance practice',
            pax='20',
            status='pending'
        )
        self.booking2 = Booking2.objects.create(
            user=self.ufacilityuser1,
            venue=self.venue2,
            date=dt.date(2050, 1, 20),
            start_time=dt.time(hour=10),
            end_time=dt.time(hour=17),
            purpose='dance practice',
            pax='20',
            status='accepted'
        )
        self.booking3 = Booking2.objects.create(
            user=self.ufacilityuser1,
            venue=self.venue2,
            date=dt.date(2050, 1, 21),
            start_time=dt.time(hour=12),
            end_time=dt.time(hour=18),
            purpose='dance practice',
            pax='20',
            status='pending'
        )
        self.booking4 = Booking2.objects.create(
            user=self.ufacilityuser0,
            venue=self.venue1,
            date=dt.date(2050, 1, 20),
            start_time=dt.time(hour=16),
            end_time=dt.time(hour=19),
            purpose='dance practice',
            pax='20',
            status='pending'
        )
        self.booking5 = Booking2.objects.create(
            user=self.ufacilityuser0,
            venue=self.venue1,
            date=dt.date(2050, 1, 21),
            start_time=dt.time(hour=16),
            end_time=dt.time(hour=19),
            purpose='dance practice',
            pax='20',
            status='declined'
        )

    def test_put_booking_success_accept(self):
        self.client0.force_authenticate(user = self.user0)
        resp = self.client0.put(
            reverse('ufacility:booking-accept', args=(1,))
        )
        # TODO
        # self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # booking = Booking2.objects.get(id=1)
        # self.assertEqual(booking.status, 'accepted')
    
    def test_put_booking_success_reject(self):
        self.client0.force_authenticate(user = self.user0)
        resp = self.client0.put(
            reverse('ufacility:booking-reject', args=(1,))
        )
        # TODO
        # self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # booking = Booking2.objects.get(id=1)
        # self.assertEqual(booking.status, 'declined')
    
    def test_put_booking_fail_accept(self):
        # cannot accept if booking has already been accepted or declined before
        self.client0.force_authenticate(user = self.user0)
        resp = self.client0.put(
            reverse('ufacility:booking-accept', args=(2,))
        )
        # TODO
        # self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
        # booking = Booking2.objects.get(id=2)
        # self.assertEqual(booking.status, 'accepted')
        # resp = self.client0.put(
        #     reverse('ufacility:booking-accept', args=(5,))
        # )
        # self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
        # booking = Booking2.objects.get(id=5)
        # self.assertEqual(booking.status, 'declined')
    
    def test_put_booking_fail_reject(self):
        # cannot reject if booking has already been accepted or declined before
        self.client0.force_authenticate(user = self.user0)
        resp = self.client0.put(
            reverse('ufacility:booking-reject', args=(2,))
        )
        # TODO
        # self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
        # booking = Booking2.objects.get(id=2)
        # self.assertEqual(booking.status, 'accepted')
        resp = self.client0.put(
            reverse('ufacility:booking-reject', args=(5,))
        )
        # TODO
        # self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
        # booking = Booking2.objects.get(id=5)
        # self.assertEqual(booking.status, 'declined')
    
    def test_put_booking_fail_forbidden(self):
        self.client1.force_authenticate(user = self.user1)
        resp = self.client1.put(
            reverse('ufacility:booking-accept', args=(1,))
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.client1.force_authenticate(user = self.user1)
        resp = self.client1.put(
            reverse('ufacility:booking-reject', args=(1,))
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_booking_fail_unauthorized(self):
        self.client2.force_authenticate(user = self.user2)
        resp = self.client2.put(
            reverse('ufacility:booking-accept', args=(1,))
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client2.force_authenticate(user = self.user2)
        resp = self.client2.put(
            reverse('ufacility:booking-reject', args=(1,))
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_put_booking_fail_not_found(self):
        self.client0.force_authenticate(user = self.user0)
        resp = self.client0.put(
            reverse('ufacility:booking-accept', args=(999,))
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
