from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework.reverse import reverse
from django.utils import timezone as tz
from datetime import timedelta as td
from json import loads
from sso.models import User


class SSOChangePasswordTest(APITestCase):

    @classmethod
    def setUpTestData(self):
        self.user1 = User.objects.create_user(
            display_name='User1',
            email='user1@e.ntu.edu.sg',
            username='user1',
            password='1048576#',
        )
        self.user2 = User.objects.create_user(
            display_name='User2',
            email='user2@e.ntu.edu.sg',
            username='user2',
            password='1048576#',
        )
        self.client1 = APIClient()
        self.client2 = APIClient()
        resp = self.client2.post(
            reverse('sso:token_obtain_pair'),
            {
                'username': 'user1',
                'password': '1048576#'
            },
            format='json'
        )
        token = loads(resp.content.decode('utf-8'))['access']
        self.client2.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
    
    def test_new_password_valid(self):
        resp = self.client2.put(
            reverse('sso:change_password'),
            {
                'new_password': '1048576#',
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.get('Content-Type'), 'application/json')
    
    def test_new_password_invalid(self):
        resp = self.client2.put(
            reverse('sso:change_password'),
            {
                'new_password': 'user2',
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.get('Content-Type'), 'application/json')


class SSOForgotPassword(APITestCase):
    
    @classmethod
    def setUpTestData(self):
        self.user1 = User.objects.create_user(
            display_name='User1',
            email='user1@e.ntu.edu.sg',
            username='user1',
            password='1048576#',
        )
        self.client = APIClient()

    def test_email_invalid(self):
        resp = self.client.post(
            reverse('sso:forgot_password'),
            {
                'email': 'user2@e.ntu.edu.sg',
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.get('Content-Type'), 'application/json')
    
    def test_email_valid(self):
        resp = self.client.post(
            reverse('sso:forgot_password'),
            {
                'email': 'USer1@e.ntu.edu.sg',
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
    
    def test_reset_valid(self):
        self.client.post(
            reverse('sso:forgot_password'),
            {
                'email': 'user1@e.ntu.edu.sg',
            },
        )
        token = User.objects.get(username='user1').custom_token
        user = User.objects.get(username='user1')
        self.assertFalse(user.is_active)

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
        self.assertGreaterEqual(tz.now() + td(days=1), user.token_expiry_date)
        self.assertTrue(user.is_active)
        
        resp3 = self.client.put(
            reverse('sso:reset_password'),
            {
                'token': token,
                'password': '4194304#',
            },
        )
        self.assertEqual(resp3.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp2.get('Content-Type'), 'application/json')
        user = User.objects.get(username='user1')
        self.assertLessEqual(user.token_expiry_date, tz.now())
    
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
