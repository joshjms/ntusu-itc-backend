# from rest_framework import status
# from rest_framework.reverse import reverse
# import datetime as dt
# from json import loads
# from ufacility.models import Booking2, Venue
# from ufacility.tests.base_test import BaseAPITestCase
# TODO - DELETE THIS

# class UfacilityVerificationsTestCase(BaseAPITestCase):
#     def setUp(self):
#         super().setUp()
#         self.venue1 = Venue.objects.create(
#             name='minerva',
#             security_email='security@mail.com',
#         )
#         self.venue2 = Venue.objects.create(
#             name='athena',
#             security_email='other_security@mail.com',
#         )
#         self.booking1 = Booking2.objects.create(
#             user=self.ufacilityuser1,
#             venue=self.venue1,
#             date=dt.date(2050, 1, 20),
#             start_time=dt.time(hour=13),
#             end_time=dt.time(hour=16),
#             purpose='dance practice',
#             pax='20',
#             status='pending'
#         )
#         self.booking2 = Booking2.objects.create(
#             user=self.ufacilityuser1,
#             venue=self.venue2,
#             date=dt.date(2050, 1, 20),
#             start_time=dt.time(hour=10),
#             end_time=dt.time(hour=17),
#             purpose='dance practice',
#             pax='20',
#             status='accepted'
#         )
#         self.booking3 = Booking2.objects.create(
#             user=self.ufacilityuser1,
#             venue=self.venue2,
#             date=dt.date(2050, 1, 21),
#             start_time=dt.time(hour=12),
#             end_time=dt.time(hour=18),
#             purpose='dance practice',
#             pax='20',
#             status='pending'
#         )
#         self.booking4 = Booking2.objects.create(
#             user=self.ufacilityuser0,
#             venue=self.venue1,
#             date=dt.date(2050, 1, 20),
#             start_time=dt.time(hour=16),
#             end_time=dt.time(hour=19),
#             purpose='dance practice',
#             pax='20',
#             status='pending'
#         )
#         self.booking5 = Booking2.objects.create(
#             user=self.ufacilityuser0,
#             venue=self.venue1,
#             date=dt.date(2050, 1, 21),
#             start_time=dt.time(hour=16),
#             end_time=dt.time(hour=19),
#             purpose='dance practice',
#             pax='20',
#             status='declined'
#         )
    
#     def test_get_bookings_fail_unauthorized(self):
#         resp = self.client3.get(
#             reverse('ufacility:bookings')
#         )
#         self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
    
#     def test_get_bookings_success_all(self):
#         self.client2.force_authenticate(user = self.user2)
#         resp = self.client2.get(
#             reverse('ufacility:bookings')
#         )
#         self.assertEqual(resp.status_code, status.HTTP_200_OK)
#         resp_json = loads(resp.content.decode('utf-8'))
        
#         # TODO 
#         # self.assertEqual(len(resp_json['bookings']), 5)
#         # self.assertEqual(resp_json['bookings'][0]['id'], 1)
#         # self.assertEqual(resp_json['bookings'][1]['id'], 2)
#         # self.assertEqual(resp_json['bookings'][2]['id'], 3)
#         # self.assertEqual(resp_json['bookings'][3]['id'], 4)
#         # self.assertEqual(resp_json['bookings'][4]['id'], 5)

#         # assert important data gained
#         # id, user display_name, venue name, data, start & end time, purpose, pax, status
#         booking = resp_json['bookings'][0]
#         # self.assertEqual(booking['id'], 1)
#         self.assertEqual(booking['user']['user']['display_name'], 'test1')
#         self.assertEqual(booking['venue']['name'], 'minerva')
#         self.assertEqual(booking['date'], '2050-01-20')
#         self.assertEqual(booking['start_time'], '13:00:00')
#         self.assertEqual(booking['end_time'], '16:00:00')
#         self.assertEqual(booking['purpose'], 'dance practice')
#         self.assertEqual(booking['pax'], 20)
#         self.assertEqual(booking['status'], 'pending')

#         # pagination related data
#         self.assertEqual(resp_json['pagination_info']['has_next'], False)
#         self.assertEqual(resp_json['pagination_info']['has_prev'], False)
#         self.assertEqual(resp_json['pagination_info']['total_pages'], 1)

#     def test_get_bookings_success_filter_1(self):
#         self.client2.force_authenticate(user = self.user2)
#         resp = self.client2.get(
#             reverse('ufacility:bookings'),
#             {
#                 'start_date': '2050-1-21'
#             }
#         )
#         self.assertEqual(resp.status_code, status.HTTP_200_OK)
#         resp_json = loads(resp.content.decode('utf-8'))
#         self.assertEqual(len(resp_json['bookings']), 2)

#         # TODO
#         # self.assertEqual(resp_json['bookings'][0]['id'], 3)
#         # self.assertEqual(resp_json['bookings'][1]['id'], 5)

#     def test_get_bookings_success_filter_2(self):
#         self.client2.force_authenticate(user = self.user2)
#         resp = self.client2.get(
#             reverse('ufacility:bookings'),
#             {
#                 'start_date': '2050-1-21',
#                 'end_date': '2050-1-20'
#             }
#         )
#         self.assertEqual(resp.status_code, status.HTTP_200_OK)
#         resp_json = loads(resp.content.decode('utf-8'))
#         self.assertEqual(len(resp_json['bookings']), 0)

#     def test_get_bookings_success_filter_3(self):
#         self.client2.force_authenticate(user = self.user2)
#         resp = self.client2.get(
#             reverse('ufacility:bookings'),
#             {
#                 'status': 'accepted-declined'
#             }
#         )
#         self.assertEqual(resp.status_code, status.HTTP_200_OK)
#         resp_json = loads(resp.content.decode('utf-8'))
#         self.assertEqual(len(resp_json['bookings']), 2)
        
#         # TODO
#         # self.assertEqual(resp_json['bookings'][0]['id'], 2)
#         # self.assertEqual(resp_json['bookings'][1]['id'], 5)

#     def test_get_bookings_success_filter_4(self):
#         self.client2.force_authenticate(user = self.user2)
#         resp = self.client2.get(
#             reverse('ufacility:bookings'),
#             {
#                 'status': 'pending',
#                 'facility': '1'
#             }
#         )
#         self.assertEqual(resp.status_code, status.HTTP_200_OK)
#         resp_json = loads(resp.content.decode('utf-8'))
        
#         # TODO
#         #self.assertEqual(len(resp_json['bookings']), 2)
#         #self.assertEqual(resp_json['bookings'][0]['id'], 1)
#         #self.assertEqual(resp_json['bookings'][1]['id'], 4)

#     def test_get_bookings_success_filter_5(self):
#         self.client2.force_authenticate(user = self.user2)
#         resp = self.client2.get(
#             reverse('ufacility:bookings'),
#             {
#                 'start_date': '2050-1-15',
#                 'end_date': '2050-1-20',
#                 'status': 'pending-accepted',
#                 'facility': '1-2'
#             }
#         )
#         self.assertEqual(resp.status_code, status.HTTP_200_OK)
#         resp_json = loads(resp.content.decode('utf-8'))

#         # TODO
#         # self.assertEqual(len(resp_json['bookings']), 3)
#         # self.assertEqual(resp_json['bookings'][0]['id'], 1)
#         # self.assertEqual(resp_json['bookings'][1]['id'], 2)
#         # self.assertEqual(resp_json['bookings'][2]['id'], 4)
    
#     def test_get_bookings_success_sort_1(self):
#         self.client2.force_authenticate(user = self.user2)
#         resp = self.client2.get(
#             reverse('ufacility:bookings'),
#             {
#                 'sort': 'desvenue__name-desend_time',
#             }
#         )
#         self.assertEqual(resp.status_code, status.HTTP_200_OK)
#         resp_json = loads(resp.content.decode('utf-8'))
#         self.assertEqual(len(resp_json['bookings']), 5)
#         # TODO
#         # self.assertEqual(resp_json['bookings'][0]['id'], 4)
#         # self.assertEqual(resp_json['bookings'][1]['id'], 5)
#         # self.assertEqual(resp_json['bookings'][2]['id'], 1)
#         # self.assertEqual(resp_json['bookings'][3]['id'], 3)
#         # self.assertEqual(resp_json['bookings'][4]['id'], 2)
    
#     def test_get_bookings_success_sort_2(self):
#         self.client2.force_authenticate(user = self.user2)
#         resp = self.client2.get(
#             reverse('ufacility:bookings'),
#             {
#                 'sort': 'desdate-ascvenue-desid',
#             }
#         )
#         self.assertEqual(resp.status_code, status.HTTP_200_OK)
#         resp_json = loads(resp.content.decode('utf-8'))
#         self.assertEqual(len(resp_json['bookings']), 5)
#         # TODO
#         # self.assertEqual(resp_json['bookings'][0]['id'], 5)
#         # self.assertEqual(resp_json['bookings'][1]['id'], 3)
#         # self.assertEqual(resp_json['bookings'][2]['id'], 4)
#         # self.assertEqual(resp_json['bookings'][3]['id'], 1)
#         # self.assertEqual(resp_json['bookings'][4]['id'], 2)

#     def test_get_bookings_success_pagination_1(self):
#         self.client2.force_authenticate(user = self.user2)
#         resp = self.client2.get(
#             reverse('ufacility:bookings'),
#             {
#                 'items_per_page': 3,
#                 'page': 1,
#             }
#         )
#         self.assertEqual(resp.status_code, status.HTTP_200_OK)
#         resp_json = loads(resp.content.decode('utf-8'))
#         self.assertEqual(len(resp_json['bookings']), 3)
#         # TODO
#         # self.assertEqual(resp_json['bookings'][0]['id'], 1)
#         # self.assertEqual(resp_json['bookings'][1]['id'], 2)
#         # self.assertEqual(resp_json['bookings'][2]['id'], 3)
#         self.assertEqual(resp_json['pagination_info']['has_next'], True)
#         self.assertEqual(resp_json['pagination_info']['has_prev'], False)
#         self.assertEqual(resp_json['pagination_info']['total_pages'], 2)

#     def test_get_bookings_success_pagination_2(self):
#         self.client2.force_authenticate(user = self.user2)
#         resp = self.client2.get(
#             reverse('ufacility:bookings'),
#             {
#                 'items_per_page': 2,
#                 'page': 3,
#             }
#         )
#         self.assertEqual(resp.status_code, status.HTTP_200_OK)
#         resp_json = loads(resp.content.decode('utf-8'))
#         self.assertEqual(len(resp_json['bookings']), 1)
#         # self.assertEqual(resp_json['bookings'][0]['id'], 5)
#         self.assertEqual(resp_json['pagination_info']['has_next'], False)
#         self.assertEqual(resp_json['pagination_info']['has_prev'], True)
#         self.assertEqual(resp_json['pagination_info']['total_pages'], 3)
