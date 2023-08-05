from json import loads
from indexswapper.tests.base_test import IndexSwapperBaseTestCase


class SwapRequestGetTestCase(IndexSwapperBaseTestCase):
    ENDPOINT = '/indexswapper/swaprequest/'

    def test_fail_unauthorized(self):
        resp = self.client3.get(self.ENDPOINT)
        self.assertEqual(resp.status_code, 401)

    def test_success_empty(self):
        resp = self.client1.get(self.ENDPOINT)
        self.assertEqual(resp.status_code, 200)
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp_json, [])

    def test_success_default(self):
        resp = self.user1c.get(self.ENDPOINT)
        self.assertEqual(resp.status_code, 200)
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(len(resp_json), 2)
        self.assertEqual(list(resp_json[0].keys()),
                         ['id', 'datetime_added', 'datetime_found', 'wanted_indexes', 'current_index',
                          'course_code', 'pair_contact_info', 'pair_contact_type',
                          'contact_info', 'contact_type', 'status', 'index_gained', 'user', 'pair'])
        self.assertEqual(resp_json[0]['wanted_indexes'], [
                         '70182', '70183', '70184'])
        self.assertEqual(resp_json[0]['current_index'], '70181')
        self.assertEqual(resp_json[0]['course_code'], 'MH1100')
        self.assertEqual(resp_json[0]['pair_contact_info'], 'user2@mail.com')
        self.assertEqual(resp_json[0]['pair_contact_type'], 'E')
        self.assertEqual(resp_json[0]['contact_info'], '@user1zzz')
        self.assertEqual(resp_json[0]['contact_type'], 'T')
        self.assertEqual(resp_json[0]['status'], 'W')
        self.assertEqual(resp_json[0]['index_gained'], '70184')
        self.assertEqual(resp_json[0]['pair'], 3)
        self.assertEqual(resp_json[1]['current_index'], '70221')
        self.assertEqual(resp_json[1]['status'], 'S')

    def test_success_qp_1(self):
        resp = self.user1c.get(self.ENDPOINT, {
            'status': 'W'
        })
        self.assertEqual(resp.status_code, 200)
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(len(resp_json), 1)
        self.assertEqual(resp_json[0]['status'], 'W')

    def test_success_qp_2(self):
        resp = self.user1c.get(self.ENDPOINT, {
            'status': 'W'
        })
        self.assertEqual(resp.status_code, 200)
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(len(resp_json), 1)
        self.assertEqual(resp_json[0]['status'], 'W')

    def test_success_qp_3(self):
        resp = self.user4c.get(self.ENDPOINT, {
            'status': 'S'
        })
        self.assertEqual(resp.status_code, 200)
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(len(resp_json), 0)
        resp = self.user4c.get(self.ENDPOINT, {
            'status': 'C'
        })
        self.assertEqual(resp.status_code, 200)
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(len(resp_json), 1)
        self.assertEqual(resp_json[0]['status'], 'C')
