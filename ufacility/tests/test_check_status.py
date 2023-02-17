from rest_framework import status
from ufacility.tests.base_test import BaseAPITestCase
from rest_framework.reverse import reverse
from json import loads


class UfacilityCheckStatusTestCase(BaseAPITestCase):
    def test_get_check_status_admin(self):
        self.client0.force_authenticate(user = self.user0)
        resp = self.client0.get(reverse('ufacility:check-user-status'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp_json["type"], "ufacility admin")

    def test_get_check_status_ufacility_user(self):
        self.client1.force_authenticate(user = self.user1)
        resp = self.client1.get(reverse('ufacility:check-user-status'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp_json["type"], "ufacility user")

    def test_get_check_status_sso_user(self):
        self.client2.force_authenticate(user = self.user2)
        resp = self.client2.get(reverse('ufacility:check-user-status'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp_json["type"], "sso user")

    def test_get_check_status_anonymous(self):
        resp = self.client3.get(reverse('ufacility:check-user-status'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp_json["type"], "anonymous")

