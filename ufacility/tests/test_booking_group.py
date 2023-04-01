from rest_framework import status
from rest_framework.reverse import reverse
import datetime as dt
from json import loads
from ufacility.models import Booking2, Venue
from ufacility.tests.base_test import BaseAPITestCase


class UfacilityVerificationsTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.client0.force_authenticate(user = self.user0)
        self.client1.force_authenticate(user = self.user1)
        self.client2.force_authenticate(user = self.user2)
        self.venue1 = Venue.objects.create(
            id='1',
            name='minerva',
            is_send_security_mail=True,
        )
        self.venue2 = Venue.objects.create(
            id='2',
            name='athena',
            is_send_security_mail=True,
        )
        self.client1.post(
            reverse('ufacility:booking-group'),
            {
                'start_time': '11:00',
                'end_time': '13:00',
                'purpose': 'coding practice',
                'pax': '11',
                'start_date': '2023-02-27',
                'end_date': '2023-03-03',
                'recurring': 'ALL',
                'venue': 1,
            }
        )
        self.client1.post(
            reverse('ufacility:booking-group'),
            {
                'start_time': '10:00',
                'end_time': '15:00',
                'purpose': 'secret stuff',
                'pax': '7',
                'start_date': '2023-02-27',
                'end_date': '2023-03-13',
                'recurring': 'MON',
                'venue': 2,
            }
        )
        self.client0.post(
            reverse('ufacility:booking-group'),
            {
                'start_time': '13:00',
                'end_time': '16:00',
                'purpose': 'dance practice',
                'pax': '20',
                'start_date': '2023-02-28',
                'end_date': '2023-03-21',
                'recurring': 'TUE',
                'venue': 1,
            }
        )
    
    def test_get_booking_groups_fail_unauthorized(self):
        resp = self.client3.get(
            reverse('ufacility:booking-group')
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_booking_groups_fail_forbidden(self):
        resp = self.client2.get(
            reverse('ufacility:booking-group')
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_booking_groups_success_all(self):
        resp = self.client1.get(
            reverse('ufacility:booking-group'),
            {
                'venue': 1,
            }
        )
        resp_json = loads(resp.content.decode('utf-8'))
        print(resp_json)
    
    def test_get_bookings_groups_success_filter(self):
        pass
    
    # def test_get_booking_groups_all
    
    # def test_get_bookings_success_all(self):
    #     self.client2.force_authenticate(user = self.user2)
    #     resp = self.client2.get(
    #         reverse('ufacility:bookings')
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)
    #     resp_json = loads(resp.content.decode('utf-8'))
        
    #     # TODO 
    #     # self.assertEqual(len(resp_json['bookings']), 5)
    #     # self.assertEqual(resp_json['bookings'][0]['id'], 1)
    #     # self.assertEqual(resp_json['bookings'][1]['id'], 2)
    #     # self.assertEqual(resp_json['bookings'][2]['id'], 3)
    #     # self.assertEqual(resp_json['bookings'][3]['id'], 4)
    #     # self.assertEqual(resp_json['bookings'][4]['id'], 5)

    #     # assert important data gained
    #     # id, user display_name, venue name, data, start & end time, purpose, pax, status
    #     booking = resp_json['bookings'][0]
    #     # self.assertEqual(booking['id'], 1)
    #     self.assertEqual(booking['user']['user']['display_name'], 'test1')
    #     self.assertEqual(booking['venue']['name'], 'minerva')
    #     self.assertEqual(booking['date'], '2050-01-20')
    #     self.assertEqual(booking['start_time'], '13:00:00')
    #     self.assertEqual(booking['end_time'], '16:00:00')
    #     self.assertEqual(booking['purpose'], 'dance practice')
    #     self.assertEqual(booking['pax'], 20)
    #     self.assertEqual(booking['status'], 'pending')

    #     # pagination related data
    #     self.assertEqual(resp_json['pagination_info']['has_next'], False)
    #     self.assertEqual(resp_json['pagination_info']['has_prev'], False)
    #     self.assertEqual(resp_json['pagination_info']['total_pages'], 1)

    # def test_get_bookings_success_filter_1(self):
    #     self.client2.force_authenticate(user = self.user2)
    #     resp = self.client2.get(
    #         reverse('ufacility:bookings'),
    #         {
    #             'start_date': '2050-1-21'
    #         }
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)
    #     resp_json = loads(resp.content.decode('utf-8'))
    #     self.assertEqual(len(resp_json['bookings']), 2)

    #     # TODO
    #     # self.assertEqual(resp_json['bookings'][0]['id'], 3)
    #     # self.assertEqual(resp_json['bookings'][1]['id'], 5)

    # def test_get_bookings_success_filter_2(self):
    #     self.client2.force_authenticate(user = self.user2)
    #     resp = self.client2.get(
    #         reverse('ufacility:bookings'),
    #         {
    #             'start_date': '2050-1-21',
    #             'end_date': '2050-1-20'
    #         }
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)
    #     resp_json = loads(resp.content.decode('utf-8'))
    #     self.assertEqual(len(resp_json['bookings']), 0)

    # def test_get_bookings_success_filter_3(self):
    #     self.client2.force_authenticate(user = self.user2)
    #     resp = self.client2.get(
    #         reverse('ufacility:bookings'),
    #         {
    #             'status': 'accepted-declined'
    #         }
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)
    #     resp_json = loads(resp.content.decode('utf-8'))
    #     self.assertEqual(len(resp_json['bookings']), 2)
        
    #     # TODO
    #     # self.assertEqual(resp_json['bookings'][0]['id'], 2)
    #     # self.assertEqual(resp_json['bookings'][1]['id'], 5)

    # def test_get_bookings_success_filter_4(self):
    #     self.client2.force_authenticate(user = self.user2)
    #     resp = self.client2.get(
    #         reverse('ufacility:bookings'),
    #         {
    #             'status': 'pending',
    #             'facility': '1'
    #         }
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)
    #     resp_json = loads(resp.content.decode('utf-8'))
        
    #     # TODO
    #     #self.assertEqual(len(resp_json['bookings']), 2)
    #     #self.assertEqual(resp_json['bookings'][0]['id'], 1)
    #     #self.assertEqual(resp_json['bookings'][1]['id'], 4)

    # def test_get_bookings_success_filter_5(self):
    #     self.client2.force_authenticate(user = self.user2)
    #     resp = self.client2.get(
    #         reverse('ufacility:bookings'),
    #         {
    #             'start_date': '2050-1-15',
    #             'end_date': '2050-1-20',
    #             'status': 'pending-accepted',
    #             'facility': '1-2'
    #         }
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)
    #     resp_json = loads(resp.content.decode('utf-8'))

    #     # TODO
    #     # self.assertEqual(len(resp_json['bookings']), 3)
    #     # self.assertEqual(resp_json['bookings'][0]['id'], 1)
    #     # self.assertEqual(resp_json['bookings'][1]['id'], 2)
    #     # self.assertEqual(resp_json['bookings'][2]['id'], 4)
    
    # def test_get_bookings_success_sort_1(self):
    #     self.client2.force_authenticate(user = self.user2)
    #     resp = self.client2.get(
    #         reverse('ufacility:bookings'),
    #         {
    #             'sort': 'desvenue__name-desend_time',
    #         }
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)
    #     resp_json = loads(resp.content.decode('utf-8'))
    #     self.assertEqual(len(resp_json['bookings']), 5)
    #     # TODO
    #     # self.assertEqual(resp_json['bookings'][0]['id'], 4)
    #     # self.assertEqual(resp_json['bookings'][1]['id'], 5)
    #     # self.assertEqual(resp_json['bookings'][2]['id'], 1)
    #     # self.assertEqual(resp_json['bookings'][3]['id'], 3)
    #     # self.assertEqual(resp_json['bookings'][4]['id'], 2)
    
    # def test_get_bookings_success_sort_2(self):
    #     self.client2.force_authenticate(user = self.user2)
    #     resp = self.client2.get(
    #         reverse('ufacility:bookings'),
    #         {
    #             'sort': 'desdate-ascvenue-desid',
    #         }
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)
    #     resp_json = loads(resp.content.decode('utf-8'))
    #     self.assertEqual(len(resp_json['bookings']), 5)
    #     # TODO
    #     # self.assertEqual(resp_json['bookings'][0]['id'], 5)
    #     # self.assertEqual(resp_json['bookings'][1]['id'], 3)
    #     # self.assertEqual(resp_json['bookings'][2]['id'], 4)
    #     # self.assertEqual(resp_json['bookings'][3]['id'], 1)
    #     # self.assertEqual(resp_json['bookings'][4]['id'], 2)

    # def test_get_bookings_success_pagination_1(self):
    #     self.client2.force_authenticate(user = self.user2)
    #     resp = self.client2.get(
    #         reverse('ufacility:bookings'),
    #         {
    #             'items_per_page': 3,
    #             'page': 1,
    #         }
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)
    #     resp_json = loads(resp.content.decode('utf-8'))
    #     self.assertEqual(len(resp_json['bookings']), 3)
    #     # TODO
    #     # self.assertEqual(resp_json['bookings'][0]['id'], 1)
    #     # self.assertEqual(resp_json['bookings'][1]['id'], 2)
    #     # self.assertEqual(resp_json['bookings'][2]['id'], 3)
    #     self.assertEqual(resp_json['pagination_info']['has_next'], True)
    #     self.assertEqual(resp_json['pagination_info']['has_prev'], False)
    #     self.assertEqual(resp_json['pagination_info']['total_pages'], 2)

    # def test_get_bookings_success_pagination_2(self):
    #     self.client2.force_authenticate(user = self.user2)
    #     resp = self.client2.get(
    #         reverse('ufacility:bookings'),
    #         {
    #             'items_per_page': 2,
    #             'page': 3,
    #         }
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)
    #     resp_json = loads(resp.content.decode('utf-8'))
    #     self.assertEqual(len(resp_json['bookings']), 1)
    #     # self.assertEqual(resp_json['bookings'][0]['id'], 5)
    #     self.assertEqual(resp_json['pagination_info']['has_next'], False)
    #     self.assertEqual(resp_json['pagination_info']['has_prev'], True)
    #     self.assertEqual(resp_json['pagination_info']['total_pages'], 3)
