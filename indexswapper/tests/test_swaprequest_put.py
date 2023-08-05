from json import loads
from indexswapper.models import SwapRequest
from indexswapper.tests.base_test import IndexSwapperBaseTestCase


class SwapRequestCreateTestCase(IndexSwapperBaseTestCase):
    ENDPOINT = (
        lambda _, id: f'/indexswapper/swaprequest/{id}/')

    def test_fail_unauthorized(self):
        resp = self.client3.put(self.ENDPOINT(2), {
            'contact_info': 'sample_mail_edit@mail.com',
            'contact_type': 'E',
        })
        self.assertEqual(resp.status_code, 401)

    def test_fail_not_found(self):
        resp = self.user1c.put(self.ENDPOINT(99999), {
            'contact_info': 'sample_mail_edit@mail.com',
            'contact_type': 'E',
        })
        self.assertEqual(resp.status_code, 404)

    def test_fail_forbidden(self):
        resp = self.user1c.put(self.ENDPOINT(3), {
            'contact_info': 'sample_mail_edit@mail.com',
            'contact_type': 'E',
        })
        self.assertEqual(resp.status_code, 403)

    def test_fail_wrong_status(self):
        # completed status
        resp = self.user4c.put(self.ENDPOINT(6), {
            'contact_info': 'sample_mail_edit@mail.com',
            'contact_type': 'E',
        })
        self.assertEqual(resp.status_code, 400)

    def test_fail_bad_request_format_1(self):
        resp = self.user1c.put(self.ENDPOINT(2), {
            'contact_info': 'sample_mail_edit@mail.com',
            'contact_type': 'Z',
        })
        self.assertEqual(resp.status_code, 400)

    def test_fail_bad_request_format_2(self):
        resp = self.user1c.put(self.ENDPOINT(2), {
            'contact_type': 'T',
        })
        self.assertEqual(resp.status_code, 400)

    def test_success(self):
        resp = self.user1c.put(self.ENDPOINT(2), {
            'contact_info': 'sample_mail_edit@mail.com',
            'contact_type': 'E',
            # extra fields below should not change anything
            'status': 'C',
            'wanted_indexes': 'ZZZZZ',
        })
        self.assertEqual(resp.status_code, 200)
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(list(resp_json.keys()), [
                         'contact_info', 'contact_type'])
        self.assertEqual(resp_json['contact_info'],
                         'sample_mail_edit@mail.com')
        self.assertEqual(resp_json['contact_type'], 'E')
        sr = SwapRequest.objects.get(id=2)
        self.assertEqual(sr.contact_info, 'sample_mail_edit@mail.com')
        self.assertEqual(sr.contact_type, 'E')
        self.assertEqual(sr.status, SwapRequest.Status.SEARCHING)
        self.assertEqual(sr.get_wanted_indexes, ['70220'])
