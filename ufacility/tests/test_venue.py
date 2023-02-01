from rest_framework import status
from ufacility.tests.base_test import BaseAPITestCase
from rest_framework.reverse import reverse


class UfacilityVenuesTestCase(BaseAPITestCase):
    def test_get_venues_success(self):
        self.client1.force_authenticate(user = self.user1)
        resp = self.client1.get(reverse('ufacility:venues'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_post_venue_success(self):
        self.client0.force_authenticate(user = self.user0)
        resp = self.client0.post(
            reverse('ufacility:venues'),
            {
                'name': 'test venue',
                'security_email': 'security@e.ntu.edu.sg',
            },
            format = 'json',
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_post_venue_fail_unauthorized(self):
        self.client2.force_authenticate(user = self.user2)
        resp = self.client2.post(
            reverse('ufacility:venues'),
            {}
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_venue_fail_forbidden(self):
        self.client1.force_authenticate(user = self.user1)
        resp = self.client1.post(
            reverse('ufacility:venues'),
            {}
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_venue_fail_bad_request_1(self):
        self.client0.force_authenticate(user = self.user0)
        resp = self.client0.post(
            reverse('ufacility:venues'),
            {
                'security_email': 'security@e.ntu.edu.sg'
            },
            format = 'json'
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_venue_fail_bad_request_2(self):
        self.client0.force_authenticate(user = self.user0)
        resp = self.client0.post(
            reverse('ufacility:venues'),
            {
                'name': 'test venue',
                'security_email': 'not an email',
            },
            format = 'json'
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
