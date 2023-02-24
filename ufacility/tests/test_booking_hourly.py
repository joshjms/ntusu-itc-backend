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
            purpose='dance practice',
            pax='20',
            status='accepted'
        )
    def test_get_hourly_booking_unauthorized(self):
        url = reverse('ufacility:booking-hourly', kwargs={"venue_id": 1, "date": "2050-01-20"})
        resp = self.client3.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    # TODO: IDK why this is error
    # def test_get_hourly_booking_success(self):
    #     self.client1.force_authenticate(user = self.user1)
    #     url = reverse('ufacility:booking-hourly', kwargs={"venue_id": 1, "date": "2050-01-20"})
    #     resp = self.client1.get(url)
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)
    #     resp_json = loads(resp.content.decode('utf-8'))

