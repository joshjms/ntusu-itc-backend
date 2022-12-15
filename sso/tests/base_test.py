from rest_framework.test import APIClient, APITestCase
from rest_framework.reverse import reverse
from json import loads
from sso.models import User


class BaseAPITestCase(APITestCase):
    '''
    Inherits from rest_framework APITestCase,
    provides setUpTestData class method that has 3 users
    (user1 as superuser, user2 & user3 as regular users),
    3 different clients for testing purpose as follows:
    Client 1 -> superuser (logged in as user1)
    Client 2 -> regular user (logged in as user2)
    Client 3 -> unauthorized / anonymous user (not logged in)
    '''
    @classmethod
    def setUpTestData(self):
        self.user1 = User.objects.create_superuser(
            display_name='User1',
            email='user1@e.ntu.edu.sg',
            username='user1',
            password='1048576#',
        )
        self.user2 = User.objects.create_user(
            display_name='User2',
            email='usER2@e.ntu.edu.sg',
            username='user2',
            password='2097152#',
        )
        self.user3 = User.objects.create_user(
            display_name='User3',
            email='user3@e.ntu.edu.sg',
            username='user3',
            password='4194304#',
        )
        self.client1 = APIClient()
        self.client2 = APIClient()
        self.client3 = APIClient()
        resp1 = self.client1.post(
            reverse('sso:token_obtain_pair'),
            {
                'username': 'user1',
                'password': '1048576#'
            },
            format='json'
        )
        token1 = loads(resp1.content.decode('utf-8'))['access']
        self.client1.credentials(HTTP_AUTHORIZATION='Bearer ' + token1)
        resp2 = self.client2.post(
            reverse('sso:token_obtain_pair'),
            {
                'username': 'user2',
                'password': '2097152#'
            },
            format='json'
        )
        token2 = loads(resp2.content.decode('utf-8'))['access']
        self.client2.credentials(HTTP_AUTHORIZATION='Bearer ' + token2)
