from rest_framework.test import APITestCase, APIClient
from sso.models import User
from event.models import EventAdmin

class BaseAPITestCase(APITestCase):
    # Create 3 different user as initial setup
    # user0 -> event superadmin
    # user1 -> event admin
    # user2 -> regular user

    def setUp(self):
        self.client0 = APIClient()
        self.user0 = User.objects.create_user(
            display_name = "test0",
            email = "test0@e.ntu.edu.sg",
            username = "test0",
            password = "somerandompassword123$",
        )
        self.eventadmin0 = EventAdmin.objects.create(
            user = self.user0,
            is_superadmin = True,
        )

        self.client1 = APIClient()
        self.user1 = User.objects.create_user(
            display_name = "test1",
            email = "test1@e.ntu.edu.sg",
            username = "test1",
            password = "somerandompassword123$",
        )
        self.eventadmin1 = EventAdmin.objects.create(
            user = self.user1,
            is_superadmin = False,
        )

        self.client2 = APIClient()
        self.user2 = User.objects.create_user(
            display_name = "test2",
            email = "test2@e.ntu.edu.sg",
            username = "test2",
            password = "somerandompassword123$",
        )