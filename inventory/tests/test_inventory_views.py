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
    # test item detail view
    def test_item_detail(self):
        # superuser can view item detail
        resp1 = self.client1.get(
            reverse('inventory:item-detail', args=(1,))
        )
        self.assertEqual(resp1.status_code, status.HTTP_200_OK)
        # regular user can view item detail
        resp2 = self.client2.get(
            reverse('inventory:item-detail', args=(1,))
        )
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        # unotherized user cannot view item detail
        resp3 = self.client3.get(
            reverse('inventory:item-detail', args=(1,))
        )
        self.assertEqual(resp3.status_code, status.HTTP_401_UNAUTHORIZED)