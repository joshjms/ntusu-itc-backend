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
    # test send loan request view
    def test_loan_request_create(self):
        # regular can send loan request
        resp1 = self.client2.post(
            reverse('inventory:loan-request-create'),
            {
                'item': 1,
                'start_date': "2030-03-01",
                'end_date': "2050-03-01",
                'quantity': 5,
            }
        )
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)
        
        # unotherized user cannot send loan request
        resp2 = self.client3.post(
            reverse('inventory:loan-request-create'),
            {
                'item': 1,
                'start_date': "2030-03-01",
                'end_date': "2050-03-01",
                'quantity': 5,
            }
        )
        self.assertEqual(resp2.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # item not found
        resp3 = self.client2.post(
            reverse('inventory:loan-request-create'),
            {
                'item': 100,
                'start_date': "2030-03-01",
                'end_date': "2050-03-01",
                'quantity': 5,
            }
        )
        self.assertEqual(resp3.status_code, status.HTTP_404_NOT_FOUND)
        
        # not enough items available
        resp4 = self.client2.post(
            reverse('inventory:loan-request-create'),
            {
                'item': 1,
                'start_date': "2030-03-01",
                'end_date': "2050-03-01",
                'quantity': 100,
            }
        )
        self.assertEqual(resp4.status_code, status.HTTP_400_BAD_REQUEST)