from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework.reverse import reverse
from sso.models import User


class SSORegisterTest(APITestCase):
    
    @classmethod
    def setUpTestData(self):
        self.user1 = User.objects.create_user(
            display_name='User1',
            email='USER1@e.ntu.edu.sg',
            username='user1',
        )
        self.client = APIClient()
    
    def test_name_blank(self):
        resp = self.client.post(
            reverse('sso:register'),
            {
                'display_name': '',
                'email': 'mich0107@e.ntu.edu.sg',
                'password': '1048576#',
            },
            format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.get('Content-Type'), 'application/json')
    
    def test_name_overlength(self):
        resp = self.client.post(
            reverse('sso:register'),
            {
                'display_name': 'abcdefghijabcdefghijabcdefghijabcdefghija',
                'email': 'mich0107@e.ntu.edu.sg',
                'password': '1048576#',
            },
            format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.get('Content-Type'), 'application/json')
    
    def test_email_blank(self):
        resp = self.client.post(
            reverse('sso:register'),
            {
                'display_name': 'Michael',
                'email': '',
                'password': '1048576#',
            },
            format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.get('Content-Type'), 'application/json')
    
    def test_email_not_ntu(self):
        resp = self.client.post(
            reverse('sso:register'),
            {
                'display_name': '',
                'email': 'mich0107@gmail.com',
                'password': '1048576#'
            },
            format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.get('Content-Type'), 'application/json')
    
    def test_email_duplicate(self):
        resp = self.client.post(
            reverse('sso:register'),
            {
                'display_name': 'some name...',
                'email': 'user1@e.ntu.edu.sg',
                'password': '1048576#'
            },
            format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.get('Content-Type'), 'application/json')
    
    def test_password_missing(self):
        resp = self.client.post(
            reverse('sso:register'),
            {
                'display_name': 'Michael',
                'email': 'mich0107@e.ntu.edu.sg',
            },
            format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.get('Content-Type'), 'application/json')

    def test_password_invalid_1(self):
        resp = self.client.post(
            reverse('sso:register'),
            {
                'display_name': '',
                'email': 'mich0107@e.ntu.edu.sg',
                'password': 'k#h8oP0'
            },
            format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.get('Content-Type'), 'application/json')

    def test_password_invalid_2(self):
        resp = self.client.post(
            reverse('sso:register'),
            {
                'display_name': '',
                'email': 'mich0107@e.ntu.edu.sg',
                'password': '9578301283'
            },
            format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.get('Content-Type'), 'application/json')
    
    def test_password_invalid_3(self):
        resp = self.client.post(
            reverse('sso:register'),
            {
                'display_name': '',
                'email': 'mich0107@e.ntu.edu.sg',
                'password': 'password'
            },
            format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.get('Content-Type'), 'application/json')

    def test_password_invalid_4(self):
        resp = self.client.post(
            reverse('sso:register'),
            {
                'display_name': '',
                'email': 'mich0107@e.ntu.edu.sg',
                'password': 'mich0107##'
            },
            format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.get('Content-Type'), 'application/json')

    def test_invalid_method(self):
        resp = self.client.get(
            reverse('sso:register'),
            {
                'display_name': 'Michael',
                'email': 'mich0107x@e.ntu.edu.sg',
                'password': '1048576#'
            },
            format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(resp.get('Content-Type'), 'application/json')
    
    def test_valid(self):
        resp = self.client.post(
            reverse('sso:register'),
            {
                'display_name': 'Michael',
                'email': 'miCH0107x@e.ntu.edu.sg',
                'password': '1048576#'
            },
            format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.get('Content-Type'), 'application/json')
        user = User.objects.get(username='mich0107x')
        self.assertFalse(user.is_active)
        self.assertEqual(user.email, 'mich0107x@e.ntu.edu.sg')


class SSOVerifyTest(APITestCase):
    
    @classmethod
    def setUpTestData(self):
        self.client = APIClient()
        self.client.post(
            reverse('sso:register'),
            {
                'display_name': 'user1',
                'email': 'user1@e.ntu.edu.sg',
                'password': '1048576#'
            },
            format='json'
        )
        self.user = User.objects.get(username='user1')
    
    def test_token_invalid(self):
        resp = self.client.post(
            reverse('sso:verify'),
            {
                'token': '123',
            },
            format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.get('Content-Type'), 'application/json')
    
    def test_token_valid(self):
        resp = self.client.post(
            reverse('sso:verify'),
            {
                'token': self.user.custom_token,
            },
            format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.get('Content-Type'), 'application/json')
        user = User.objects.get(username='user1')
        self.assertTrue(user.is_active)
