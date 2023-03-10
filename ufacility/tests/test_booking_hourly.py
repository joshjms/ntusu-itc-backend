from rest_framework import status
from rest_framework.reverse import reverse
import datetime as dt
from json import loads
from ufacility.models import Booking2, Venue
from ufacility.tests.base_test import BaseAPITestCase


class UfacilityBookingHourlyTestCase(BaseAPITestCase):
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
            purpose='coding practice',
            pax='13',
            status='accepted'
        )
        self.booking3 = Booking2.objects.create(
            user=self.ufacilityuser1,
            venue=self.venue2,
            date=dt.date(2050, 1, 21),
            start_time=dt.time(hour=13),
            end_time=dt.time(hour=16),
            purpose='dance practice',
            pax='20',
            status='accepted'
        )
    
    def test_get_hourly_booking_unauthorized(self):
        url = reverse('ufacility:booking-hourly', kwargs={'venue_id': self.venue1.id, 'date': '2050-01-20'})
        resp = self.client3.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_hourly_booking_success_1(self):
        self.client1.force_authenticate(user = self.user1)
        url = reverse('ufacility:booking-hourly', kwargs={'venue_id': self.venue1.id, 'date': '2050-01-20'})
        resp = self.client1.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(len(resp_json), 1)
        self.assertEqual(resp.data[0]['user_email'], 'test1@e.ntu.edu.sg')
        self.assertEqual(resp.data[0]['user_cca'], 'su')
        self.assertEqual(resp.data[0]['start_time'], '13:00:00')
        self.assertEqual(resp.data[0]['end_time'], '16:00:00')
        self.assertEqual(resp.data[0]['purpose'], 'dance practice')
        self.assertEqual(resp.data[0]['pax'], 20)
        self.assertEqual(resp.data[0]['status'], 'pending')

    def test_get_hourly_booking_success_2(self):
        self.client1.force_authenticate(user = self.user1)
        url = reverse('ufacility:booking-hourly', kwargs={'venue_id': self.venue1.id, 'date': '2050-01-21'})
        resp = self.client1.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(len(resp_json), 0)

    def test_get_hourly_booking_fail_bad_request(self):
        self.client1.force_authenticate(user = self.user1)
        # incorrect date format give
        url = reverse('ufacility:booking-hourly', kwargs={'venue_id': self.venue1.id, 'date': '21-01-2050'})
        resp = self.client1.get(url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_hourly_booking_fail_venue_not_found(self):
        self.client1.force_authenticate(user = self.user1)
        url = reverse('ufacility:booking-hourly', kwargs={'venue_id': 999, 'date': '2050-01-21'})
        resp = self.client1.get(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
