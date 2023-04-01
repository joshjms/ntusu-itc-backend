from rest_framework import status
from rest_framework.reverse import reverse
from ufacility.tests.base_test import BaseAPITestCase
from ufacility.models import Venue


class UfacilityVerificationDetailsTestCase(BaseAPITestCase):
    @classmethod
    def setUpTestData(self):
        self.venue1 = Venue.objects.create(
            name='Minerva',
            is_send_security_mail=True,
        )
    
    def test_put_venue_success(self):
        self.client0.force_authenticate(user = self.user0)
        url = reverse('ufacility:venue-detail', kwargs={'pk': 1})
        response = self.client0.put(url, {
            'name': 'Minerva_edit',
            'is_send_security_mail': False,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Minerva_edit')
        self.assertEqual(response.data['is_send_security_mail'], False)
    
    def test_put_venue_fail_bad_request_1(self):
        self.client0.force_authenticate(user = self.user0)
        url = reverse('ufacility:venue-detail', kwargs={'pk': self.venue1.id})
        response = self.client0.put(url, {
            'name': 'some invalid venue name longer then 30 characters',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_venue_fail_bad_request_2(self):
        self.client0.force_authenticate(user = self.user0)
        url = reverse('ufacility:venue-detail', kwargs={'pk': self.venue1.id})
        response = self.client0.put(url, {
            'name': 'Minerva_edit',
            'is_send_security_mail': 'someothervaluenotbool',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_venue_fail_unauthorized(self):
        self.client2.force_authenticate(user = self.user2)
        url = reverse('ufacility:venue-detail', kwargs={'pk': self.venue1.id})
        response = self.client2.put(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_put_venue_fail_forbidden(self):
        self.client1.force_authenticate(user = self.user1)
        url = reverse('ufacility:venue-detail', kwargs={'pk': self.venue1.id})
        response = self.client1.put(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_venue_fail_not_found(self):
        self.client0.force_authenticate(user = self.user0)
        url = reverse('ufacility:venue-detail', kwargs={'pk': 999})
        response = self.client0.put(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
