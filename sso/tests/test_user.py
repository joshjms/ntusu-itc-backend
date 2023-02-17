from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from json import loads
from sso.tests.base_test import BaseAPITestCase


class SSOUserProfileTest(BaseAPITestCase):
    # get user's profile
    def test_user_get(self):
        resp = self.client.get(
            reverse('sso:user', args=('user1',))
        )
        # TODO (I think the id is no longer 1)
        # self.assertJSONEqual(
        #     str(resp.content, encoding='utf8'),
        #     {
        #         'id': 1,
        #         'username': 'user1',
        #         'email': 'user1@e.ntu.edu.sg',
        #         'display_name': 'User1',
        #         'description': '',
        #     }
        # )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
    
    # getting refresh and access token if verification completed
    def test_jwt_token_valid(self):
        resp = self.client.post(
            reverse('sso:token_obtain_pair'),
            {
                'username': 'user2',
                'password': '2097152#'
            },
            format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp_dict = loads(resp.content.decode('utf-8'))
        self.assertTrue('refresh' in resp_dict)
        self.assertTrue('access' in resp_dict)
    
    # verification failed (incorrect username / password)
    def test_jwt_token_invalid(self):
        resp = self.client.post(
            reverse('sso:token_obtain_pair'),
            {
                'username': 'user2',
                'password': '1048576'
            },
            format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(resp.get('Content-Type'), 'application/json')
    
    # cannot edit profile if not logged in
    def test_user_edit_unauthorized(self):
        resp = self.client.put(
            reverse('sso:user', args=('user1',)),
            {
                'display_name': 'edit_name',
                'description': 'some description',
            }
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(resp.get('Content-Type'), 'application/json')

    # cannot edit other people's profile, cannot make your display name empty
    def test_user_edit_invalid(self):
        resp = self.client.post(
            reverse('sso:token_obtain_pair'),
            {
                'username': 'user2',
                'password': '2097152#'
            },
            format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token = loads(resp.content.decode('utf-8'))['access']
        
        client2 = APIClient()
        client2.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        resp2 = client2.put(
            reverse('sso:user', args=('user1',)),
            {
                'display_name': 'user2edit',
                'description': 'some description',
            },
        )
        self.assertEqual(resp2.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(resp2.get('Content-Type'), 'application/json')
        
        resp3 = client2.put(
            reverse('sso:user', args=('user2',)),
            {
                'display_name': '',
                'description': 'some description',
            },
        )
        self.assertEqual(resp3.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp3.get('Content-Type'), 'application/json')

    # get valid jwt token and correctly edit your own profile
    def test_user_edit_valid(self):
        resp = self.client.post(
            reverse('sso:token_obtain_pair'),
            {
                'username': 'user2',
                'password': '2097152#'
            },
            format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token = loads(resp.content.decode('utf-8'))['access']
        
        client2 = APIClient()
        client2.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        resp2 = client2.put(
            reverse('sso:user', args=('user2',)),
            {
                'display_name': 'user2edit',
                'description': '',
            },
        )
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertEqual(resp2.get('Content-Type'), 'application/json')
