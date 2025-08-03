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
    # test items list view
    def test_items_list(self):
        # superuser can view items
        resp1 = self.client1.get(
            reverse('inventory:items-list')
        )
        self.assertEqual(resp1.status_code, status.HTTP_200_OK)
        # regular user can view items
        resp2 = self.client2.get(
            reverse('inventory:items-list')
        )
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        # unotherized user cannot view items
        resp3 = self.client3.get(
            reverse('inventory:items-list')
        )
        self.assertEqual(resp3.status_code, status.HTTP_401_UNAUTHORIZED)