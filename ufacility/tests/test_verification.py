from rest_framework import status
from ufacility.tests.base_test import BaseAPITestCase
from rest_framework.reverse import reverse

class UfacilityVerificationsTestCase(BaseAPITestCase):
    def test_post_verification_success(self):
        self.client2.force_authenticate(user = self.user2)
        resp = self.client2.post(
            reverse("ufacility:verifications"), 
            {
                "email": "test2@e.ntu.edu.sg",
                "cca": "su",
                "role": "member",
            },
            format = "json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["email"], "test2@e.ntu.edu.sg")
        self.assertEqual(resp.data["cca"], "su")
        self.assertEqual(resp.data["role"], "member")

    def test_post_verification_fail_duplicate_verification(self):
        # First time success
        self.client2.force_authenticate(user = self.user2)
        resp = self.client2.post(
            reverse("ufacility:verifications"), 
            {
                "email": "test2@e.ntu.edu.sg",
                "cca": "su",
                "role": "member",
            },
            format = "json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Second time fail
        resp = self.client2.post(
            reverse("ufacility:verifications"), 
            {
                "email": "test2@e.ntu.edu.sg",
                "cca": "su",
                "role": "member",
            },
            format = "json",
        )
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_post_verification_fail_existing_user(self):
        self.client1.force_authenticate(user = self.user1)
        resp = self.client1.post(
            reverse("ufacility:verifications"),
            {},
            format = "json",
        )
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_post_verification_fail_bad_request(self):
        self.client2.force_authenticate(user = self.user2)
        resp = self.client2.post(
            reverse("ufacility:verifications"), 
            {
                "cca": "su",
            },
            format = "json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_verifications_success(self):
        self.client0.force_authenticate(user = self.user0)
        resp = self.client0.get(reverse("ufacility:verifications"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_verifications_fail_unauthorized(self):
        self.client2.force_authenticate(user = self.user2)
        resp = self.client2.get(reverse("ufacility:verifications"))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_verifications_fail_forbidden(self):
        self.client1.force_authenticate(user = self.user1)
        resp = self.client1.get(reverse("ufacility:verifications"))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

