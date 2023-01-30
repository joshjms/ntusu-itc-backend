from rest_framework import status
from ufacility.tests.base_test import BaseAPITestCase
from rest_framework.reverse import reverse
from sso.models import User
from ufacility.models import UFacilityUser
from rest_framework.test import APIClient


class UfacilityUserDetailsTestCase(BaseAPITestCase):
    @classmethod
    def setUpTestData(self):
        self.user = User.objects.create_user(
            display_name = "test user",
            email = "testuser@e.ntu.edu.sg",
            username = "testuser",
            password = "somevalidpassword123$",
        )
        self.ufacilityuser = UFacilityUser.objects.create(
            user = self.user,
            is_admin = False,
            cca = "su",
            hongen_name = "hg",
            hongen_phone_number = "87654321",
        )
        self.client = APIClient()

    def test_get_user_details_success(self):
        # Test request as admin
        self.client0.force_authenticate(user = self.user0)
        url = reverse('ufacility:user-detail', kwargs={"user_id": self.ufacilityuser.id})
        resp = self.client0.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(list(resp.data["user"].items())[0][1], "testuser")
        self.assertEqual(resp.data["is_admin"], False)
        self.assertEqual(resp.data["cca"], "su")
        self.assertEqual(resp.data["hongen_name"], "hg")
        self.assertEqual(resp.data["hongen_phone_number"], "87654321")

        # Test request as the ufacility user itself
        self.client.force_authenticate(user = self.user)
        url = reverse('ufacility:user-detail', kwargs={"user_id": 0})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(list(resp.data["user"].items())[0][1], "testuser")
        self.assertEqual(resp.data["is_admin"], False)
        self.assertEqual(resp.data["cca"], "su")
        self.assertEqual(resp.data["hongen_name"], "hg")
        self.assertEqual(resp.data["hongen_phone_number"], "87654321")


    def test_get_user_details_fail_unauthorized(self):
        self.client2.force_authenticate(user = self.user2)
        url = reverse('ufacility:user-detail', kwargs={"user_id": self.user.id})
        resp = self.client2.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_details_fail_forbidden(self):
        self.client1.force_authenticate(user = self.user1)
        url = reverse('ufacility:user-detail', kwargs={"user_id": self.user.id})
        resp = self.client1.get(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user_details_fail_not_found(self):
        self.client0.force_authenticate(user = self.user0)
        url = reverse('ufacility:user-detail', kwargs={"user_id": 100})
        resp = self.client0.get(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
