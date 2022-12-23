from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework.reverse import reverse
from django.utils import timezone as tz
from datetime import timedelta as td
from json import loads
from sso.models import User
from sso.tests.base_test import BaseAPITestCase


class SSOChangePasswordTest(BaseAPITestCase):
    # change password route should change the password (if it is valid)
    def test_new_password_valid(self):
        resp = self.client2.put(
            reverse('sso:change_password'),
            {
                'new_password': 'somenewvalidpw',
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        user = User.objects.get(username='user2')
        self.assertTrue(user.check_password('somenewvalidpw'))
        self.assertEqual(resp.get('Content-Type'), 'application/json')
    
    # do not allow password change if new password is too weak
    def test_new_password_invalid_1(self):
        resp = self.client2.put(
            reverse('sso:change_password'),
            {
                'new_password': 'user2',
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertIsNotNone(resp_json, 'errors')
    
    # do not allow password change if new password is too weak
    def test_new_password_invalid_2(self):
        resp = self.client2.put(
            reverse('sso:change_password'),
            {
                'new_password': '12345678',
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertIsNotNone(resp_json, 'errors')


class SSOForgotPassword(BaseAPITestCase):
    # email is unregistered
    def test_email_invalid(self):
        resp = self.client.post(
            reverse('sso:forgot_password'),
            {
                'email': 'user4@e.ntu.edu.sg',
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.get('Content-Type'), 'application/json')
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp_json['detail'], 'Not found.')
    
    # if valid email, custom token should be generated and email sent
    def test_email_valid(self):
        resp = self.client.post(
            reverse('sso:forgot_password'),
            {
                'email': 'USeR1@e.ntu.edu.sg',
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.get('Content-Type'), 'application/json')
        user = User.objects.get(username='user1')
        self.assertIsNotNone(user.custom_token)
        self.assertIsNotNone(user.token_expiry_date)


class SSOResetPassword(APITestCase):
    @classmethod
    def setUpTestData(self):
        self.user1 = User.objects.create_user(
            display_name='User1',
            email='user1@e.ntu.edu.sg',
            username='user1',
            password='1048576#',
            is_active=False,
        )
        self.client = APIClient()
    
    # check password reset when password given is valid
    def test_reset_valid(self):
        # get custom token
        self.client.post(
            reverse('sso:forgot_password'),
            {
                'email': 'user1@e.ntu.edu.sg',
            },
        )
        token = User.objects.get(username='user1').custom_token
        user = User.objects.get(username='user1')
        self.assertFalse(user.is_active)

        # use custom token to reset password
        resp2 = self.client.put(
            reverse('sso:reset_password'),
            {
                'token': token,
                'password': '4194304#',
            },
        )
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertEqual(resp2.get('Content-Type'), 'application/json')
        user = User.objects.get(username='user1')
        self.assertIsNotNone(user.custom_token)
        self.assertTrue(user.check_password('4194304#'))
        self.assertGreaterEqual(tz.now() + td(days=0.1), user.token_expiry_date)
        self.assertTrue(user.is_active)
        
        # token can only be used once
        resp3 = self.client.put(
            reverse('sso:reset_password'),
            {
                'token': token,
                'password': '4194304#new',
            },
        )
        resp_json = loads(resp3.content.decode('utf-8'))
        self.assertEqual(resp_json['non_field_errors'][0], 'token already used')
        self.assertEqual(resp3.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp3.get('Content-Type'), 'application/json')
    
    # reset password response when invalid token is given
    def test_reset_invalid_token(self):
        resp = self.client.put(
            reverse('sso:reset_password'),
            {
                'token': 'abcde',
                'password': '4194304#',
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.get('Content-Type'), 'application/json')

    # when new password is invalid or too weak
    def test_reset_invalid_password(self):
        self.client.post(
            reverse('sso:forgot_password'),
            {
                'email': 'user1@e.ntu.edu.sg',
            },
        )
        token = User.objects.get(username='user1').custom_token
        
        resp2 = self.client.put(
            reverse('sso:reset_password'),
            {
                'token': token,
                'password': '12345678',
            },
        )
        self.assertEqual(resp2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp2.get('Content-Type'), 'application/json')
        user = User.objects.get(username='user1')
        self.assertLessEqual(tz.now() + td(days=0.9), user.token_expiry_date)


class SSOVerifyTokenTest(APITestCase):
    @classmethod
    def setUpTestData(self):
        # create user
        self.user1 = User.objects.create_user(
            display_name='User1',
            email='user1@e.ntu.edu.sg',
            username='user1',
            password='1048576#',
        )
        self.client = APIClient()
        # get custom token
        self.client.post(
            reverse('sso:forgot_password'),
            {
                'email': 'user1@e.ntu.edu.sg',
            },
        )
        self.token = User.objects.get(username='user1').custom_token
    
    def test_token_invalid(self):
        # token is not valid (no user has this token), must return 404
        resp = self.client.get(
            reverse('sso:verify_token', args=(12345678901234567890,))
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
    
    # TODO - using mock or freezegun library to simulate time
    # def test_token_expired(self):
    #     # pretend that token has already expired, must return 401
    #     user = User.objects.get(username='user1')
    #     print(user.token_expiry_date)
    #     user.token_expiry_date = tz.now() + td(days=2)
    #     print(user.token_expiry_date)
    #     user.save()
    #     a = User.objects.get(username='user1')
    #     print(a.token_expiry_date)
    #     resp = self.client.get(
    #         reverse('sso:verify_token', args=(self.token,))
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_valid(self):
        # token is valid
        resp = self.client.get(
            reverse('sso:verify_token', args=(self.token,))
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
