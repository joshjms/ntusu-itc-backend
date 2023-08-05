'''
    This file is used to:
    - ensure email operation can be completed successfully given data of the intended structure format
    - test email stylings by sending emails to your own email (change line 14 below to test it!)
'''
from indexswapper.models import SwapRequest
from indexswapper.tests.base_test import IndexSwapperBaseTestCase
from indexswapper.utils import email


class SwapRequestEmailTestCase(IndexSwapperBaseTestCase):
    # change this to your email to send email template to yourself
    TEST_EMAIL = 'testmail@e.ntu.edu.sg'

    @classmethod
    def setUpTestData(self):
        super().setUpTestData()
        self.SAMPLE_SWAP_REQUEST: SwapRequest = SwapRequest.objects.get(id=3)
        self.SAMPLE_SWAP_REQUEST.user.email = self.TEST_EMAIL
        self.SAMPLE_SWAP_REQUEST.user.save()

    def test_email_send_swap_search_creation(self):
        resp = email.send_swap_request_creation(self.SAMPLE_SWAP_REQUEST)
        self.assertEqual(resp['ResponseMetadata']['HTTPStatusCode'], 200)

    def test_email_send_swap_search_another(self):
        resp = email.send_swap_search_another(self.SAMPLE_SWAP_REQUEST)
        self.assertEqual(resp['ResponseMetadata']['HTTPStatusCode'], 200)

    def test_email_send_swap_cancel_self(self):
        resp = email.send_swap_cancel_self(self.SAMPLE_SWAP_REQUEST)
        self.assertEqual(resp['ResponseMetadata']['HTTPStatusCode'], 200)

    def test_email_send_swap_cancel_pair(self):
        # take note that in views.py, this function is called for your pair
        # e.g., call `send_swap_cancel_pair(instance.pair)``
        resp = email.send_swap_cancel_pair(self.SAMPLE_SWAP_REQUEST)
        self.assertEqual(resp['ResponseMetadata']['HTTPStatusCode'], 200)

    def test_email_send_swap_completed(self):
        resp = email.send_swap_completed(self.SAMPLE_SWAP_REQUEST)
        self.assertEqual(resp['ResponseMetadata']['HTTPStatusCode'], 200)

    def test_email_send_swap_pair_found(self):
        resp = email.send_swap_pair_found(self.SAMPLE_SWAP_REQUEST)
        self.assertEqual(resp['ResponseMetadata']['HTTPStatusCode'], 200)
