from rest_framework import status
from rest_framework.reverse import reverse
from json import loads
from ufacility.models import Verification
from ufacility.tests.base_test import BaseAPITestCase


class UfacilityVerificationsTestCase(BaseAPITestCase):
    def test_post_verification_success(self):
        self.client2.force_authenticate(user = self.user2)
        resp = self.client2.post(
            reverse('ufacility:verifications'), 
            {
                'cca': 'ntusu_itc',
                'hongen_name': 'bc',
                'hongen_phone_number': '61235874',
            },
            format = 'json',
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['cca'], 'ntusu_itc')
        self.assertEqual(resp.data['hongen_name'], 'bc')
        self.assertEqual(resp.data['hongen_phone_number'], '61235874')
        self.assertEqual(resp.data['status'], 'pending')
        self.assertEqual(resp.data['user']['id'], self.user2.id)
        # self.assertEqual(resp.data['id'], 1) TODO
        self.assertEqual(Verification.objects.all().count(), 1)

    def test_post_verification_fail_duplicate_verification(self):
        # First time success
        self.client2.force_authenticate(user = self.user2)
        resp = self.client2.post(
            reverse('ufacility:verifications'), 
            {
                'cca': 'su',
                'hongen_name': 'bc',
                'hongen_phone_number': '91235874',
            },
            format = 'json',
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['cca'], 'su')
        self.assertEqual(resp.data['hongen_name'], 'bc')
        self.assertEqual(resp.data['hongen_phone_number'], '91235874')
        self.assertEqual(resp.data['status'], 'pending')

        # Second time fail
        resp = self.client2.post(
            reverse('ufacility:verifications'), 
            {
                'cca': 'su',
                'hongen_name': 'bc',
                'hongen_phone_number': '91235874',
            },
            format = 'json',
        )
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_post_verification_fail_existing_user(self):
        self.client1.force_authenticate(user = self.user1)
        resp = self.client1.post(
            reverse('ufacility:verifications'),
            {
                'cca': 'example_cca',
                'hongen_name': 'example_hongen_name',
                'hongen_phone_number': '12345678',
            },
            format = 'json',
        )
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_post_verification_fail_bad_request(self):
        self.client2.force_authenticate(user = self.user2)

        # missing fields
        resp1 = self.client2.post(
            reverse('ufacility:verifications'), 
            {
                'cca': 'su',
            },
            format = 'json',
        )
        self.assertEqual(resp1.status_code, status.HTTP_400_BAD_REQUEST)

        # invalid phone number (not sg phone num)
        resp2 = self.client2.post(
            reverse('ufacility:verifications'), 
            {
                'cca': 'su',
                'hongen_name': 'some name',
                'hongen_phone_number': '12345678'
            },
            format = 'json',
        )
        self.assertEqual(resp2.status_code, status.HTTP_400_BAD_REQUEST)

        # name too long (name and cca only max 30 chars)
        resp3 = self.client2.post(
            reverse('ufacility:verifications'), 
            {
                'cca': 'su',
                'hongen_name': 'some string longer than 30 chars is unacceptable',
                'hongen_phone_number': '12345678'
            },
            format = 'json',
        )
        self.assertEqual(resp3.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_post_fail_unauthorized(self):
        resp = self.client3.post(
            reverse('ufacility:verifications'), 
            {
                'cca': 'su',
                'hongen_name': 'joshua',
                'hongen_phone_number': '61537239'
            },
            format = 'json',
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_verifications_success(self):
        Verification.objects.create(
            user=self.user2,
            cca='cca',
            hongen_name='somename',
            hongen_phone_number='87654321',
            status='pending'
        )
        self.client0.force_authenticate(user = self.user0)
        resp = self.client0.get(reverse('ufacility:verifications'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(len(resp_json), 1)
    
    def test_get_verifications_success_filter(self):
        v1 = Verification.objects.create(
            user=self.user2,
            cca='cca',
            hongen_name='somename',
            hongen_phone_number='87654321',
            status='pending'
        )
        v2 = Verification.objects.create(
            user=self.user1,
            cca='cca',
            hongen_name='somename',
            hongen_phone_number='87654321',
            status='accepted'
        )
        v3 = Verification.objects.create(
            user=self.user0,
            cca='cca',
            hongen_name='somename',
            hongen_phone_number='87654321',
            status='pending'
        )
        self.client0.force_authenticate(user = self.user0)
        resp = self.client0.get(reverse('ufacility:verifications'), {
            'status': 'declined-pending'
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(len(resp_json), 2)
        self.assertEqual(resp_json[0]['id'], v1.id)
        self.assertEqual(resp_json[1]['id'], v3.id)
        resp = self.client0.get(reverse('ufacility:verifications'), {
            'status': 'declined'
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(len(resp_json), 0)

    def test_get_verifications_fail_unauthorized(self):
        self.client2.force_authenticate(user = self.user2)
        resp1 = self.client2.get(reverse('ufacility:verifications'))
        self.assertEqual(resp1.status_code, status.HTTP_401_UNAUTHORIZED)

        resp2 = self.client3.get(reverse('ufacility:verifications'))
        self.assertEqual(resp2.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_verifications_fail_forbidden(self):
        self.client1.force_authenticate(user = self.user1)
        resp = self.client1.get(reverse('ufacility:verifications'))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
