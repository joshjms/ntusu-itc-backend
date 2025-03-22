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