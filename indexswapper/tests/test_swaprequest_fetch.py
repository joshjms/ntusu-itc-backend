from json import loads
from unittest.mock import patch
from indexswapper.models import SwapRequest
from indexswapper.tests.base_test import IndexSwapperBaseTestCase


class SwapRequestSearchAnotherTestCase(IndexSwapperBaseTestCase):
    ENDPOINT = (
        lambda _, id: f'/indexswapper/swaprequest/{id}/search_another/')
    CREATE_ENDPOINT = '/indexswapper/swaprequest/'

    def test_fail_unauthorized(self):
        resp = self.client3.patch(self.ENDPOINT(1))
        self.assertEqual(resp.status_code, 401)

    def test_fail_pk_not_int(self):
        resp = self.user1c.patch(self.ENDPOINT('abc'))
        self.assertEqual(resp.status_code, 400)

    def test_fail_not_found(self):
        resp = self.user1c.patch(self.ENDPOINT(99999))
        self.assertEqual(resp.status_code, 404)

    def test_fail_forbidden(self):
        resp = self.user1c.patch(self.ENDPOINT(3))
        self.assertEqual(resp.status_code, 403)

    def test_fail_not_waiting_status_1(self):
        # still searching
        resp = self.user1c.patch(self.ENDPOINT(2))
        self.assertEqual(resp.status_code, 400)

    def test_fail_not_waiting_status_2(self):
        # completed status
        resp = self.user4c.patch(self.ENDPOINT(6))
        self.assertEqual(resp.status_code, 400)

    def test_fail_cooldown_unfinished(self):
        # note: we only simply test failure if we search another right after making the first swaprequest
        # assume that the `COOLDOWN_HOURS` in `verify_cooldown` decorator is at least 1 hour
        resp = self.client1.post(self.CREATE_ENDPOINT, {
            'contact_info': 'sample_mail@mail.com',
            'contact_type': 'E',
            'current_index_num': '70220',
            'wanted_indexes': ['70221', '70217'],
        })
        self.assertEqual(resp.status_code, 201)
        resp_json = loads(resp.content.decode('utf-8'))
        resp2 = self.client1.patch(self.ENDPOINT(resp_json['id']))
        self.assertEqual(resp2.status_code, 400)
        resp_json_2 = loads(resp2.content.decode('utf-8'))
        self.assertEqual(resp_json_2['error'], 'waiting for cooldown')
        self.assertGreater(float(resp_json_2['time_left']), 0)
        self.assertEqual(list(resp_json_2.keys()), ['error', 'time_left'])

    @patch('indexswapper.utils.email.send_swap_search_another')
    @patch('indexswapper.utils.email.send_swap_pair_found')
    def test_success_pair_found(self, mock_func1, mock_func2):
        SWAPREQUEST_ID = 1
        instance = SwapRequest.objects.get(id=SWAPREQUEST_ID)
        old_pair_id = instance.pair.id
        new_sr_resp = self.client2.post(self.CREATE_ENDPOINT, {
            'contact_info': 'sample_mail@mail.com',
            'contact_type': 'E',
            'current_index_num': '70184',
            'wanted_indexes': ['70181', '70192'],
        })
        resp = self.user1c.patch(self.ENDPOINT(SWAPREQUEST_ID))
        self.assertEqual(resp.status_code, 200)
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp_json['is_pair_success'], True)
        instance = SwapRequest.objects.get(id=SWAPREQUEST_ID)
        self.assertEqual(instance.status, SwapRequest.Status.WAITING)
        self.assertEqual(instance.index_gained, '70184')
        self.assertEqual(instance.pair.id, new_sr_resp.data['id'])
        self.assertEqual(instance.pair.status, SwapRequest.Status.WAITING)
        self.assertEqual(instance.pair.index_gained, '70181')
        self.assertIsNotNone(instance.pair.datetime_found)
        self.assertIsNotNone(instance.datetime_added)
        self.assertIsNotNone(instance.datetime_found)
        self.assertEqual(instance.datetime_found, instance.pair.datetime_found)
        old_pair = SwapRequest.objects.get(id=old_pair_id)
        self.assertEqual(old_pair.pair.id, SWAPREQUEST_ID)
        self.assertEqual(old_pair.status, SwapRequest.Status.REVOKED)
        mock_func1.assert_called()
        self.assertEqual(mock_func1.call_count, 2)
        mock_func2.assert_called_once()

    @patch('indexswapper.utils.email.send_swap_search_another')
    def test_success_pair_not_found(self, mock_func):
        SWAPREQUEST_ID = 1
        instance = SwapRequest.objects.get(id=SWAPREQUEST_ID)
        old_pair_id = instance.pair.id
        resp = self.user1c.patch(self.ENDPOINT(SWAPREQUEST_ID))
        self.assertEqual(resp.status_code, 200)
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp_json['is_pair_success'], False)
        instance = SwapRequest.objects.get(id=SWAPREQUEST_ID)
        self.assertEqual(instance.status, SwapRequest.Status.SEARCHING)
        self.assertEqual(instance.index_gained, '')
        self.assertIsNone(instance.datetime_found)
        self.assertIsNone(instance.pair)
        self.assertIsNotNone(instance.datetime_added)
        old_pair = SwapRequest.objects.get(id=old_pair_id)
        self.assertEqual(old_pair.pair.id, SWAPREQUEST_ID)
        self.assertEqual(old_pair.status, SwapRequest.Status.REVOKED)
        mock_func.assert_called_once()


class SwapRequestMarkCompleteTestCase(IndexSwapperBaseTestCase):
    ENDPOINT = (lambda _, id: f'/indexswapper/swaprequest/{id}/mark_complete/')

    def test_fail_unauthorized(self):
        resp = self.client3.patch(self.ENDPOINT(1))
        self.assertEqual(resp.status_code, 401)

    def test_fail_not_found(self):
        resp = self.user1c.patch(self.ENDPOINT(99999))
        self.assertEqual(resp.status_code, 404)

    def test_fail_forbidden(self):
        resp = self.user1c.patch(self.ENDPOINT(3))
        self.assertEqual(resp.status_code, 403)

    def test_fail_not_waiting_status_1(self):
        # already completed
        resp = self.user4c.patch(self.ENDPOINT(6))
        self.assertEqual(resp.status_code, 400)

    def test_fail_not_waiting_status_2(self):
        # still searching
        resp = self.user1c.patch(self.ENDPOINT(2))
        self.assertEqual(resp.status_code, 400)

    @patch('indexswapper.utils.email.send_swap_completed')
    def test_success(self, mock_func):
        resp = self.user1c.patch(self.ENDPOINT(1))
        self.assertEqual(resp.status_code, 200)
        swap_request = SwapRequest.objects.get(id=1)
        self.assertEqual(swap_request.status, SwapRequest.Status.COMPLETED)
        pair_swap_request = swap_request.pair
        self.assertEqual(pair_swap_request.status,
                         SwapRequest.Status.COMPLETED)
        mock_func.assert_called_once()


class SwapRequestCancelSwapTestCase(IndexSwapperBaseTestCase):
    ENDPOINT = (lambda _, id: f'/indexswapper/swaprequest/{id}/cancel_swap/')
    CREATE_ENDPOINT = '/indexswapper/swaprequest/'

    def test_fail_unauthorized(self):
        resp = self.client3.patch(self.ENDPOINT(1))
        self.assertEqual(resp.status_code, 401)

    def test_fail_not_found(self):
        resp = self.user1c.patch(self.ENDPOINT(99999))
        self.assertEqual(resp.status_code, 404)

    def test_fail_forbidden(self):
        resp = self.user1c.patch(self.ENDPOINT(3))
        self.assertEqual(resp.status_code, 403)

    def test_fail_completed_status(self):
        # already completed
        resp = self.user4c.patch(self.ENDPOINT(6))
        self.assertEqual(resp.status_code, 400)

    @patch('indexswapper.utils.email.send_swap_cancel_self')
    @patch('indexswapper.utils.email.send_swap_cancel_pair')
    def test_success_status_waiting_1(self, mock_func1, mock_func2):
        resp = self.user1c.patch(self.ENDPOINT(1))
        self.assertEqual(resp.status_code, 200)
        swap_request = SwapRequest.objects.get(id=1)
        self.assertEqual(swap_request.status, SwapRequest.Status.REVOKED)
        self.assertEqual(swap_request.index_gained, '70184')
        self.assertIsNotNone(swap_request.datetime_found)
        self.assertEqual(swap_request.pair.status,
                         SwapRequest.Status.SEARCHING)
        self.assertEqual(swap_request.pair.id, 3)
        self.assertEqual(swap_request.pair.index_gained, '')
        self.assertIsNone(swap_request.pair.pair)
        self.assertIsNone(swap_request.pair.datetime_found)
        mock_func1.assert_called_once()
        mock_func2.assert_called_once()

    @patch('indexswapper.utils.email.send_swap_cancel_self')
    @patch('indexswapper.utils.email.send_swap_cancel_pair')
    def test_success_status_waiting_2(self, mock_func1, mock_func2):
        # pair found match after researching
        new_sr_resp = self.client1.post(self.CREATE_ENDPOINT, {
            'contact_info': 'sample_mail@mail.com',
            'contact_type': 'E',
            'current_index_num': '70185',
            'wanted_indexes': ['70181', '70184'],
        })
        new_sr_resp_json = loads(new_sr_resp.content.decode('utf-8'))
        resp = self.user1c.patch(self.ENDPOINT(1))
        self.assertEqual(resp.status_code, 200)
        swap_request = SwapRequest.objects.get(id=1)
        self.assertEqual(swap_request.status, SwapRequest.Status.REVOKED)
        self.assertEqual(swap_request.index_gained, '70184')
        self.assertIsNotNone(swap_request.datetime_found)
        self.assertEqual(swap_request.pair.status,
                         SwapRequest.Status.WAITING)
        self.assertEqual(swap_request.pair.pair.id, new_sr_resp_json['id'])
        self.assertEqual(swap_request.pair.index_gained, '70185')
        self.assertIsNotNone(swap_request.pair.pair)
        self.assertIsNotNone(swap_request.pair.datetime_found)
        instance = SwapRequest.objects.get(id=new_sr_resp_json['id'])
        self.assertEqual(instance.status, SwapRequest.Status.WAITING)
        self.assertEqual(instance.pair, swap_request.pair)
        self.assertEqual(instance.index_gained, '70184')
        mock_func1.assert_called_once()
        mock_func2.assert_called_once()

    @patch('indexswapper.utils.email.send_swap_cancel_self')
    def test_success_status_searching(self, mock_func):
        resp = self.user1c.patch(self.ENDPOINT(2))
        self.assertEqual(resp.status_code, 200)
        swap_request = SwapRequest.objects.get(id=2)
        self.assertEqual(swap_request.status, SwapRequest.Status.REVOKED)
        self.assertIsNone(swap_request.pair)
        mock_func.assert_called_once()
