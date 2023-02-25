from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from ufacility.tests.base_test import BaseAPITestCase
from ufacility.models import UFacilityUser
from sso.models import User


class UfacilityUserDetailsTestCase(BaseAPITestCase):
    @classmethod
    def setUpTestData(self):
        self.user = User.objects.create_user(
            display_name = 'test user',
            email = 'testuser@e.ntu.edu.sg',
            username = 'testuser',
            password = 'somevalidpassword123$',
        )
        self.ufacilityuser = UFacilityUser.objects.create(
            user = self.user,
            is_admin = False,
            cca = 'su',
            hongen_name = 'hg',
            hongen_phone_number = '87654321',
        )
        self.client = APIClient()

    def test_get_user_details_success(self):
        # test request as admin
        self.client0.force_authenticate(user = self.user0)
        url = reverse('ufacility:user-detail', kwargs={'user_id': self.ufacilityuser.id})
        resp = self.client0.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['is_admin'], False)
        self.assertEqual(resp.data['cca'], 'su')
        self.assertEqual(resp.data['hongen_name'], 'hg')
        self.assertEqual(resp.data['hongen_phone_number'], '87654321')

        # test request as the ufacility user itself
        self.client.force_authenticate(user = self.user)
        url = reverse('ufacility:user-detail', kwargs={'user_id': 0})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['is_admin'], False)
        self.assertEqual(resp.data['cca'], 'su')
        self.assertEqual(resp.data['hongen_name'], 'hg')
        self.assertEqual(resp.data['hongen_phone_number'], '87654321')
    
    def test_get_own_instance_success(self):
        # get own information (admin)
        self.client0.force_authenticate(user = self.user0)
        url = reverse('ufacility:user-detail', kwargs={'user_id': 0})
        resp = self.client0.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['is_admin'], True)
        self.assertEqual(resp.data['cca'], 'su')
        self.assertEqual(resp.data['hongen_name'], 'hongen')
        self.assertEqual(resp.data['hongen_phone_number'], '92348754')

        # get own information (ufacility user)
        self.client1.force_authenticate(user = self.user1)
        url = reverse('ufacility:user-detail', kwargs={'user_id': 0})
        resp = self.client1.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['is_admin'], False)
        self.assertEqual(resp.data['cca'], 'su')
        self.assertEqual(resp.data['hongen_name'], 'hongen2')
        self.assertEqual(resp.data['hongen_phone_number'], '82348759')

    def test_get_user_details_fail_forbidden(self):
        self.client2.force_authenticate(user = self.user2)
        url = reverse('ufacility:user-detail', kwargs={'user_id': self.user.id})
        resp = self.client2.get(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        self.client2.force_authenticate(user = self.user1)
        url = reverse('ufacility:user-detail', kwargs={'user_id': self.user.id})
        resp = self.client2.get(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user_details_fail_not_found(self):
        self.client0.force_authenticate(user = self.user0)
        url = reverse('ufacility:user-detail', kwargs={'user_id': 100})
        resp = self.client0.get(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_user_details_success(self):
        # test request as admin
        self.client0.force_authenticate(user = self.user0)
        url = reverse('ufacility:user-detail', kwargs={'user_id': self.ufacilityuser0.id})
        resp = self.client0.put(url, {
            'cca': 'su_edit',
            'hongen_name': 'hongen new',
            'hongen_phone_number': '80001234',
            'is_admin': False, # this should not affect anything
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['is_admin'], True)
        self.assertEqual(resp.data['cca'], 'su')
        self.assertEqual(resp.data['hongen_name'], 'hongen new')
        self.assertEqual(resp.data['hongen_phone_number'], '80001234')

        # test request as the ufacility user itself
        self.client1.force_authenticate(user = self.user1)
        url = reverse('ufacility:user-detail', kwargs={'user_id': self.ufacilityuser1.id})
        resp = self.client1.put(url, {
            'cca': 'su_edit',
            'hongen_name': 'hongen new new new',
            'hongen_phone_number': '87654321',
            'is_admin': True, # this should not affect anything
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['is_admin'], False)
        self.assertEqual(resp.data['cca'], 'su')
        self.assertEqual(resp.data['hongen_name'], 'hongen new new new')
        self.assertEqual(resp.data['hongen_phone_number'], '87654321')

    def test_put_user_details_fail_forbidden(self):
        # non ufacility user cannot edit
        self.client2.force_authenticate(user = self.user2)
        url = reverse('ufacility:user-detail', kwargs={'user_id': self.ufacilityuser1.id})
        send_json = {
            'cca': 'cca_edit',
            'hongen_name': 'hongen_edit',
            'hongen_phone_number': '87654321',
        }
        resp = self.client2.put(url, send_json)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # regular ufacility user cannot edit other user's profile
        self.client.force_authenticate(user = self.user)
        resp = self.client.put(url, send_json)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_user_details_fail_bad_request(self):
        # invalid hongen name (empty)
        self.client1.force_authenticate(user = self.user1)
        url = reverse('ufacility:user-detail', kwargs={'user_id': self.ufacilityuser1.id})
        resp = self.client1.put(url, {
            'cca': 'su_edit',
            'hongen_name': '',
            'hongen_phone_number': '87654321',
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        # invalid phone number
        self.client1.force_authenticate(user = self.user1)
        url = reverse('ufacility:user-detail', kwargs={'user_id': self.ufacilityuser1.id})
        resp = self.client1.put(url, {
            'cca': 'su_edit',
            'hongen_name': 'name',
            'hongen_phone_number': '07654321',
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
