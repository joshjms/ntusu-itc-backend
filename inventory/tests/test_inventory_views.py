from sso.tests.base_test import BaseAPITestCase
from rest_framework.reverse import reverse
from rest_framework import status

from inventory.models import (
    InventoryUser,
    InventoryLender,
    Item,
    ItemLoanRequest,
)

class InventoryViewTest(BaseAPITestCase):
    # test user loan requests list view
    def test_user_loan_requests_list(self):
        # superuser can view user loan requests
        resp1 = self.client1.get(
            reverse('inventory:user-loan-requests', args=('user1',))
        )
        self.assertEqual(resp1.status_code, status.HTTP_200_OK)
        
        # regular user can view own loan requests
        resp2 = self.client2.get(
            reverse('inventory:user-loan-requests', args=('user2',))
        )
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        # regular user cannot view other user's loan requests
        resp3 = self.client2.get(
            reverse('inventory:user-loan-requests', args=('user3',))
        )
        self.assertEqual(resp3.status_code, status.HTTP_403_FORBIDDEN)
        
        # unotherized user cannot view user loan requests
        resp4 = self.client3.get(
            reverse('inventory:user-loan-requests', args=('user1',))
        )
        self.assertEqual(resp4.status_code, status.HTTP_401_UNAUTHORIZED)