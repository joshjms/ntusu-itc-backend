from rest_framework.test import APITestCase, APIClient
from sso.models import User
from ufacility.models import UFacilityUser


'''
    Provide 3 clients as follows:
    self.client0: UFacility Admin
    self.client1: UFacility User
    self.client2: Regular SSO User
    self.client3: Anonymous User
'''
class BaseAPITestCase(APITestCase):
    def setUp(self):
        self.client0 = APIClient()
        self.user0 = User.objects.create_user(
            display_name = 'test0',
            email = 'test0@e.ntu.edu.sg',
            username = 'test0',
            password = 'somerandompassword123$',
        )
        self.ufacilityuser0 = UFacilityUser.objects.create(
            user = self.user0,
            is_admin = True,
            cca = 'su',
            hongen_name = 'hongen',
            hongen_phone_number = '12348754',
        )

        self.client1 = APIClient()
        self.user1 = User.objects.create_user(
            display_name = 'test1',
            email = 'test1@e.ntu.edu.sg',
            username = 'test1',
            password = 'somerandompassword123$',
        )
        self.ufacilityuser1 = UFacilityUser.objects.create(
            user = self.user1,
            is_admin = False,
            cca = 'su',
            hongen_name = 'hongen2',
            hongen_phone_number = '12348759',
        )

        self.client2 = APIClient()
        self.user2 = User.objects.create_user(
            display_name = 'test2',
            email = 'test2@e.ntu.edu.sg',
            username = 'test2',
            password = 'somerandompassword123$',
        )

        self.client3 = APIClient()
