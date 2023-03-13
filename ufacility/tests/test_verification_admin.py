from rest_framework import status
from rest_framework.reverse import reverse
from ufacility.tests.base_test import BaseAPITestCase
from ufacility.models import Verification, UFacilityUser


class UfacilityVerificationAdminTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.client2.force_authenticate(user = self.user2)
        resp = self.client2.post(
            reverse('ufacility:verification'), 
            {
                'cca': 'ntusu_itc_trial',
                'hongen_name': 'bc',
                'hongen_phone_number': '61235874',
            },
            format = 'json',
        )
        self.verification_sample_id = resp.data['id']
    
    def test_put_verification_accept(self):
        # accept verification for first time
        self.client0.force_authenticate(user = self.user0)
        response = self.client0.put(
            reverse('ufacility:verification-accept', args=(self.verification_sample_id,))
        )
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(response.data['message'], 'Verification accepted.')

        # ufacilityuser model should be created automatically, status becomes accepted
        verification = Verification.objects.get(id=self.verification_sample_id)
        self.assertEqual(verification.status, 'accepted')
        ufacilityuser = UFacilityUser.objects.get(user=verification.user)
        self.assertEqual(ufacilityuser.cca, 'ntusu_itc_trial')
        
        # accept verification for second time: display conflict
        response = self.client0.put(
            reverse('ufacility:verification-accept', args=(self.verification_sample_id,))
        )
        self.assertEqual(response.status_code, 409)

        # revoke access
        response = self.client0.put(
            reverse('ufacility:verification-reject', args=(self.verification_sample_id,))
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Access revoked.')

        # make sure no related ufacility user model
        ufacilityuser_count = UFacilityUser.objects.filter(user=verification.user).count()
        self.assertEqual(ufacilityuser_count, 0)
    
    def test_put_verification_reject(self):
        # reject verification
        self.client0.force_authenticate(user = self.user0)
        response = self.client0.put(
            reverse('ufacility:verification-reject', args=(self.verification_sample_id,))
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Verification rejected.')

        # status should be rejected
        verification = Verification.objects.get(id=self.verification_sample_id)
        self.assertEqual(verification.status, 'declined')
        
        # second time, display conflict
        response = self.client0.put(
            reverse('ufacility:verification-reject', args=(self.verification_sample_id,))
        )
        self.assertEqual(response.status_code, 409)

        # accept after rejection is possible
        self.client0.force_authenticate(user = self.user0)
        response = self.client0.put(
            reverse('ufacility:verification-accept', args=(self.verification_sample_id,))
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Verification accepted.')

        # ufacilityuser model should be created automatically, status becomes accepted
        verification = Verification.objects.get(id=self.verification_sample_id)
        self.assertEqual(verification.status, 'accepted')
        ufacilityuser = UFacilityUser.objects.get(user=verification.user)
        self.assertEqual(ufacilityuser.cca, 'ntusu_itc_trial')

    def test_put_verification_accept_reject_fail_forbidden(self):
        self.client1.force_authenticate(user = self.user1)
        response = self.client1.put(
            reverse('ufacility:verification-accept', args=(1,))
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client1.put(
            reverse('ufacility:verification-reject', args=(1,))
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_verification_accept_reject_fail_not_found(self):
        self.client0.force_authenticate(user = self.user0)
        response = self.client0.put(
            reverse('ufacility:verification-accept', args=(999,))
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client0.put(
            reverse('ufacility:verification-reject', args=(0,))
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
