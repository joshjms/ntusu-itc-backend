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
    # test item loan requests list view
    def test_item_loan_requests_list(self):
        # superuser can view item loan requests
        resp1 = self.client1.get(
            reverse('inventory:loan-requests-list')
        )
        self.assertEqual(resp1.status_code, status.HTTP_200_OK)
        
        # regular user cannot view item loan requests
        resp2 = self.client2.get(
            reverse('inventory:loan-requests-list')
        )
        self.assertEqual(resp2.status_code, status.HTTP_403_FORBIDDEN)
        
        # unotherized user cannot view item loan requests
        resp3 = self.client3.get(
            reverse('inventory:loan-requests-list')
        )
        self.assertEqual(resp3.status_code, status.HTTP_401_UNAUTHORIZED)