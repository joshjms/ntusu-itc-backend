from rest_framework import status
from rest_framework.reverse import reverse
from json import loads
from ufacility.tests.base_test import BaseAPITestCase
from ufacility.models import Verification
from sso.models import User


class UfacilityVerificationDetailsTestCase(BaseAPITestCase):
    @classmethod
    def setUpTestData(self):
        self.verification1 = Verification.objects.create(
            user = User.objects.create_user(
                display_name = 'test',
                email = 'test@e.ntu.edu.sg',
                username = 'test',
                password = 'somevalidpassword123$',
            ),
            cca =  'su',
            hongen_name = 'bc',
            hongen_phone_number = '12345678',
            status = 'pending'
        )

    def test_get_verification_detail_success(self):
        self.client0.force_authenticate(user = self.user0)
        verification = Verification.objects.all()[0]
        url = reverse('ufacility:verification-detail', kwargs={'verification_id': verification.id})
        response = self.client0.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resp_json = loads(response.content.decode('utf-8'))
        self.assertEqual(resp_json['id'], self.verification1.id)
        self.assertEqual(resp_json['cca'], 'su')
        self.assertEqual(resp_json['hongen_name'], 'bc')
        self.assertEqual(resp_json['hongen_phone_number'], '12345678')
        self.assertEqual(resp_json['status'], 'pending')
        self.assertEqual(resp_json['user']['username'], 'test')
        self.assertEqual(resp_json['user']['email'], 'test@e.ntu.edu.sg')
        self.assertEqual(resp_json['user']['display_name'], 'test')

    def test_get_verification_detail_fail_forbidden_1(self):
        self.client2.force_authenticate(user = self.user2)
        url = reverse('ufacility:verification-detail', kwargs={'verification_id': 1})
        response = self.client2.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_verification_detail_fail_forbidden_2(self):
        self.client1.force_authenticate(user = self.user1)
        url = reverse('ufacility:verification-detail', kwargs={'verification_id': 1})
        response = self.client1.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_verification_detail_fail_not_found(self):
        self.client0.force_authenticate(user = self.user0)
        url = reverse('ufacility:verification-detail', kwargs={'verification_id': 100})
        response = self.client0.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # def test_put_verification_detail_success(self):
    #     self.client0.force_authenticate(user = self.user0)
    #     verification = Verification.objects.all()[0]
    #     url = reverse('ufacility:verification-detail', kwargs={'verification_id': verification.id})
    #     response = self.client0.put(
    #         url,
    #         {
    #             'email': 'new@e.ntu.edu.sg',
    #             'cca': 'new su',
    #         },
    #         format = 'json',
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['cca'], 'new su')
    #     self.assertEqual(response.data['hongen_name'], 'bc')
    #     self.assertEqual(response.data['hongen_phone_number'], '12345678')

    # def test_put_verification_detail_fail_unauthorized(self):
    #     self.client2.force_authenticate(user = self.user2)
    #     url = reverse('ufacility:verification-detail', kwargs={'verification_id': 1})
    #     response = self.client2.put(
    #         url,
    #         {}
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_put_verification_detail_fail_forbidden(self):
    #     self.client1.force_authenticate(user = self.user1)
    #     url = reverse('ufacility:verification-detail', kwargs={'verification_id': 1})
    #     response = self.client1.put(
    #         url,
    #         {}
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_put_verification_detail_fail_not_found(self):
    #     self.client0.force_authenticate(user = self.user0)
    #     url = reverse('ufacility:verification-detail', kwargs={'verification_id': 100})
    #     response = self.client0.put(
    #         url,
    #         {}
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_verification_detail_success(self):
        self.client0.force_authenticate(user = self.user0)
        verification = Verification.objects.all()[0]
        url = reverse('ufacility:verification-detail', kwargs={'verification_id': verification.id})
        response = self.client0.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_verification_detail_fail_forbidden_1(self):
        self.client2.force_authenticate(user = self.user2)
        url = reverse('ufacility:verification-detail', kwargs={'verification_id': 1})
        response = self.client2.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_verification_detail_fail_forbidden_2(self):
        self.client1.force_authenticate(user = self.user1)
        url = reverse('ufacility:verification-detail', kwargs={'verification_id': 1})
        response = self.client1.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_verification_detail_fail_not_found(self):
        self.client0.force_authenticate(user = self.user0)
        url = reverse('ufacility:verification-detail', kwargs={'verification_id': 100})
        response = self.client0.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
