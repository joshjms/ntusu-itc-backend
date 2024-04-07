from rest_framework.test import APITestCase, APIClient
from sso.models import User
from ulocker.models import ULockerAdmin, Locker, Location, Booking

'''
    Provide 2 clients as follows:
    self.client0: Anonymous User
    self.client1: ULocker Admin
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

        self.client1 = APIClient()
        self.user1 = User.objects.create_user(
            display_name = 'test1',
            email = 'test1@e.ntu.edu.sg',
            username = 'test1',
            password = 'somerandompassword123$',
        )
        self.ulockeruser1 = ULockerAdmin.objects.create(
            user = self.user1,
            is_send_creation_email = False,
            is_send_verification_email = False,
            is_send_allocation_email = False,
        )

        self.location1 = Location.objects.create(
            location_name = 'Location 1',
        )

        self.locker1 = Locker.objects.create(
            name = 'Locker 1',
            location = self.location1,
            is_available = True,
        )

        self.locker2 = Locker.objects.create(
            name = 'Locker 2',
            location = self.location1,
            is_available = True,
        )

        self.locker_na = Locker.objects.create(
            name = 'Locker 3',
            location = self.location1,
            is_available = False,
        )