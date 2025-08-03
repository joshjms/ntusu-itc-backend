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
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        # 3 users with different roles:
        # self.client1 -> superuser (logged in as user1)
        # self.client2 -> regular user (logged in as user2)
        # self.client3 -> unauthorized / anonymous user (not logged in)
        
        # link users to inventory users
        self.inventory_user1 = InventoryUser.objects.create(
            user=self.user1,
        )
        self.inventory_user2 = InventoryUser.objects.create(
            user=self.user2,
        )
        self.inventory_user3 = InventoryUser.objects.create(
            user=self.user3,
        )
        # link users to inventory lender
        self.inventory_lender1 = InventoryLender.objects.create(
            user=self.user1,
            organisation_name='ntusu',
        )
        
        # create items
        self.item1 = Item.objects.create(
            title='item1',
            description='description1',
            category='category1',
            quantity=12,
            user=self.inventory_lender1,
        )
        self.item2 = Item.objects.create(
            title='item2',
            description='description2',
            category='category2',
            quantity=20,
            user=self.inventory_lender1,
        )
        # create item loan requests
        self.item_loan_request1 = ItemLoanRequest.objects.create(
            approval_status='processing',
            start_date='2050-01-01',
            end_date='2050-01-02',
            quantity=5,
            item=self.item1,
            user=self.inventory_user2,
        )
        self.item_loan_request2 = ItemLoanRequest.objects.create(
            approval_status='processing',
            start_date='2050-01-01',
            end_date='2050-01-02',
            quantity=5,
            item=self.item2,
            user=self.inventory_user2,
        )
        self.item_loan_request3 = ItemLoanRequest.objects.create(
            approval_status='accepted',
            start_date='2050-01-01',
            end_date='2050-01-02',
            quantity=5,
            item=self.item1,
            user=self.inventory_user3,
        )