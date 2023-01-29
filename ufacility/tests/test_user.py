from rest_framework import status
from ufacility.tests.base_test import BaseAPITestCase
from rest_framework.reverse import reverse
from sso.models import User


class UfacilityUsersTestCase(BaseAPITestCase):
    def test_post_user_success(self):
        self.client0.force_authenticate(user = self.user0)
        new_user_id = User.objects.create_user(
                    display_name = "test user",
                    email = "testuser@e.ntu.edu.sg",
                    username = "testuser",
                    password = "testuserpassword123%",
                ).id
        resp = self.client0.post(
            reverse("ufacility:users"),
            {
                "user": new_user_id,
                "cca": "su",
                "hongen_name": "hongen",
                "hongen_phone_number": "12345678",
            },
            format = "json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["user"], new_user_id)
        self.assertEqual(resp.data["cca"], "su")
        self.assertEqual(resp.data["is_admin"], False)
        self.assertEqual(resp.data["hongen_name"], "hongen")
        self.assertEqual(resp.data["hongen_phone_number"], "12345678")

    def test_post_user_fail_unauthorized(self):
        self.client2.force_authenticate(user = self.user2)
        resp = self.client2.post(
            reverse("ufacility:users"),
            {},
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_user_fail_forbidden(self):
        self.client1.force_authenticate(user = self.user1)
        resp = self.client1.post(
            reverse("ufacility:users"),
            {},
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_user_fail_bad_request(self):
        self.client0.force_authenticate(user = self.user0)
        resp = self.client0.post(
            reverse("ufacility:users"),
            {},
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

