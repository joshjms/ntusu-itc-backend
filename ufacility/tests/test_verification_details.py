from rest_framework import status
from ufacility.tests.base_test import BaseAPITestCase
from rest_framework.reverse import reverse
from ufacility.models import Verification
from sso.models import User


class UfacilityVerificationDetailsTestCase(BaseAPITestCase):
    @classmethod
    def setUpTestData(self):
        self.verification1 = Verification.objects.create(
            user = User.objects.create_user(
                display_name = "test",
                email = "test@e.ntu.edu.sg",
                username = "test",
                password = "somevalidpassword123$",
            ),
            email = "test2@e.ntu.edu.sg",
            cca = "su",
            role = "member",
        )

    def test_get_verification_detail_success(self):
        self.client0.force_authenticate(user = self.user0)
        verification = Verification.objects.all()[0]
        url = reverse('ufacility:verification-detail', kwargs={"verification_id": verification.id})
        response = self.client0.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_verification_detail_fail_unauthorized(self):
        self.client2.force_authenticate(user = self.user2)
        url = reverse('ufacility:verification-detail', kwargs={"verification_id": 1})
        response = self.client2.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_verification_detail_fail_forbidden(self):
        self.client1.force_authenticate(user = self.user1)
        url = reverse('ufacility:verification-detail', kwargs={"verification_id": 1})
        response = self.client1.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_verification_detail_fail_not_found(self):
        self.client0.force_authenticate(user = self.user0)
        url = reverse('ufacility:verification-detail', kwargs={"verification_id": 100})
        response = self.client0.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_verification_detail_success(self):
        self.client0.force_authenticate(user = self.user0)
        verification = Verification.objects.all()[0]
        url = reverse('ufacility:verification-detail', kwargs={"verification_id": verification.id})
        response = self.client0.put(
            url,
            {
                "email": "new@e.ntu.edu.sg",
                "cca": "new su",
            },
            format = "json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "new@e.ntu.edu.sg")
        self.assertEqual(response.data["cca"], "new su")
        self.assertEqual(response.data["role"], verification.role)

    def test_put_verification_detail_fail_unauthorized(self):
        self.client2.force_authenticate(user = self.user2)
        url = reverse('ufacility:verification-detail', kwargs={"verification_id": 1})
        response = self.client2.put(
            url,
            {}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_verification_detail_fail_forbidden(self):
        self.client1.force_authenticate(user = self.user1)
        url = reverse('ufacility:verification-detail', kwargs={"verification_id": 1})
        response = self.client1.put(
            url,
            {}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_verification_detail_fail_not_found(self):
        self.client0.force_authenticate(user = self.user0)
        url = reverse('ufacility:verification-detail', kwargs={"verification_id": 100})
        response = self.client0.put(
            url,
            {}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_verification_detail_success(self):
        self.client0.force_authenticate(user = self.user0)
        verification = Verification.objects.all()[0]
        url = reverse('ufacility:verification-detail', kwargs={"verification_id": verification.id})
        response = self.client0.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_verification_detail_fail_unauthorized(self):
        self.client2.force_authenticate(user = self.user2)
        url = reverse('ufacility:verification-detail', kwargs={"verification_id": 1})
        response = self.client2.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_verification_detail_fail_forbidden(self):
        self.client1.force_authenticate(user = self.user1)
        url = reverse('ufacility:verification-detail', kwargs={"verification_id": 1})
        response = self.client1.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_verification_detail_fail_not_found(self):
        self.client0.force_authenticate(user = self.user0)
        url = reverse('ufacility:verification-detail', kwargs={"verification_id": 100})
        response = self.client0.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

