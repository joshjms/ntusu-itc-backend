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
    # test return item view
    def test_loan_request_return(self):
        # superuser can modify loan request status to returned
        resp1 = self.client1.put(
            reverse('inventory:loan-request-return', args=(3,)),
        )
        self.assertEqual(resp1.status_code, status.HTTP_200_OK)
        
        # regular user cannot modify loan request status
        resp2 = self.client2.put(
            reverse('inventory:loan-request-return', args=(3,)),
        )
        self.assertEqual(resp2.status_code, status.HTTP_403_FORBIDDEN)
        
        # unotherized user cannot modify loan request status
        resp3 = self.client3.put(
            reverse('inventory:loan-request-return', args=(3,)),
        )
        self.assertEqual(resp3.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # loan request not found
        resp4 = self.client1.put(
            reverse('inventory:loan-request-return', args=(100,)),
        )
        self.assertEqual(resp4.status_code, status.HTTP_404_NOT_FOUND)
        
        # loan request has not been accepted
        resp5 = self.client1.put(
            reverse('inventory:loan-request-return', args=(1,)),
        )
        self.assertEqual(resp5.status_code, status.HTTP_400_BAD_REQUEST)