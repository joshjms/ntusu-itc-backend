from json import loads
from indexswapper.tests.base_test import IndexSwapperBaseTestCase


class CourseIndexListTestCase(IndexSwapperBaseTestCase):
    ENDPOINT = '/indexswapper/courseindex/'

    def test_fail_not_found_page(self):
        resp = self.client3.get(self.ENDPOINT, {
            'page': 999,
        })
        self.assertEqual(resp.status_code, 404)
        resp = self.client3.get(self.ENDPOINT, {
            'page': 0,
        })
        self.assertEqual(resp.status_code, 404)
        resp = self.client3.get(self.ENDPOINT, {
            'page': -1,
        })
        self.assertEqual(resp.status_code, 404)

    def test_success_default(self):
        resp = self.client3.get(self.ENDPOINT)
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp_json['count'], 33)
        self.assertEqual(resp_json['total_pages'], 4)
        self.assertEqual(len(resp_json['results']), 10)
        self.assertEqual(list(resp_json.keys()), [
                         'count', 'prev', 'next', 'total_pages', 'results'])
        self.assertEqual(list(resp_json['results'][0].keys()), [
                         'id', 'code', 'name', 'index', 'pending_count'])

    def test_success_qp_pagination(self):
        resp = self.client3.get(self.ENDPOINT, {
            'page_size': 2,
            'page': 5,
        })
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp_json['count'], 33)
        self.assertEqual(resp_json['total_pages'], 17)
        self.assertEqual(len(resp_json['results']), 2)
        self.assertEqual(resp_json['results'][0]['code'], 'MH1100')
        self.assertEqual(resp_json['results'][1]['code'], 'MH1100')

    def test_success_qp_code_icontains(self):
        resp = self.client3.get(self.ENDPOINT, {
            'code__icontains': '1100'
        })
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp_json['count'], 12)
        self.assertEqual(resp_json['total_pages'], 2)
        self.assertEqual(resp_json['results'][0]['code'], 'MH1100')

    def test_success_qp_name_icontains(self):
        resp = self.client3.get(self.ENDPOINT, {
            'name__icontains': 'math'
        })
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp_json['count'], 11)
        self.assertEqual(resp_json['total_pages'], 2)
        self.assertEqual(resp_json['results'][0]['code'], 'MH1300')

    def test_success_qp_pending_count_lte_gte(self):
        resp = self.client3.get(self.ENDPOINT, {
            'pending_count__gte': '1',
            'pending_count__lte': '2'
        })
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp_json['count'], 7)
        self.assertEqual(resp_json['total_pages'], 1)
        for result in resp_json['results']:
            self.assertTrue(result['pending_count'] >= 1)
            self.assertTrue(result['pending_count'] <= 2)

    def test_success_qp_index(self):
        resp = self.client3.get(self.ENDPOINT, {
            'index': '70218'
        })
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp_json['count'], 1)
        self.assertEqual(resp_json['total_pages'], 1)
        self.assertEqual(resp_json['results'][0]['code'], 'MH1300')
        self.assertEqual(resp_json['results'][0]['pending_count'], 2)

    def test_qp_ordering_1(self):
        resp = self.client3.get(self.ENDPOINT, {
            'ordering': 'index',
        })
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp_json['count'], 33)
        self.assertEqual(resp_json['total_pages'], 4)
        self.assertEqual(resp_json['results'][0]['index'], '70181')
        self.assertEqual(resp_json['results'][1]['index'], '70182')
        self.assertEqual(resp_json['results'][2]['index'], '70183')

    def test_qp_ordering_2(self):
        resp = self.client3.get(self.ENDPOINT, {
            'ordering': '-index',
        })
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp_json['count'], 33)
        self.assertEqual(resp_json['total_pages'], 4)
        self.assertEqual(resp_json['results'][0]['index'], '70221')
        self.assertEqual(resp_json['results'][1]['index'], '70220')
        self.assertEqual(resp_json['results'][2]['index'], '70219')

    def test_qp_ordering_3(self):
        resp = self.client3.get(self.ENDPOINT, {
            'ordering': '-name',
            'page_size': 20,
        })
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp_json['count'], 33)
        self.assertEqual(resp_json['total_pages'], 2)
        self.assertEqual(resp_json['results'][0]['name'], 'LINEAR ALGEBRA I')
        self.assertEqual(resp_json['results'][19]
                         ['name'], 'FOUNDATIONS OF MATHEMATICS')

    def test_qp_ordering_4(self):
        resp = self.client3.get(self.ENDPOINT, {
            'ordering': 'pending_count, -index',
            'pending_count__gte': 1,
        })
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp_json['count'], 8)
        self.assertEqual(resp_json['total_pages'], 1)
        self.assertEqual(resp_json['results'][0]['index'], '70204')
        self.assertEqual(resp_json['results'][1]['index'], '70203')
        self.assertEqual(resp_json['results'][2]['index'], '70201')
        self.assertEqual(resp_json['results'][5]['index'], '70181')
        self.assertEqual(resp_json['results'][6]['index'], '70218')
        self.assertEqual(resp_json['results'][7]['index'], '70220')


class CourseIndexRetrieveTestCase(IndexSwapperBaseTestCase):
    ENDPOINT = (lambda _, index: f'/indexswapper/courseindex/{index}/')

    def test_fail_invalid_index(self):
        resp = self.client3.get(self.ENDPOINT('99999'))
        self.assertEqual(resp.status_code, 404)

    def test_success_default(self):
        resp = self.client3.get(self.ENDPOINT('70181'))
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp_json['code'], 'MH1100')
        self.assertEqual(resp_json['name'], 'CALCULUS I')
        self.assertEqual(resp_json['pending_count'], 1)
        self.assertEqual(resp_json['pending_dict'], {'70191': 1})
        self.assertEqual(list(resp_json.keys()), [
                         'id', 'code', 'name', 'index', 'datetime_added',
                         'information_data', 'pending_count', 'pending_dict'])
        self.assertEqual(len(resp_json['information_data']), 18)
        self.assertEqual(list(resp_json['information_data'][0].keys()),
                         ['type', 'group', 'day', 'time', 'venue', 'remark'])

    def test_success_2(self):
        resp = self.client3.get(self.ENDPOINT('70220'))
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp_json['code'], 'MH1300')
        self.assertEqual(resp_json['name'], 'FOUNDATIONS OF MATHEMATICS')
        self.assertEqual(resp_json['pending_count'], 3)
        self.assertEqual(resp_json['pending_dict'], {'70215': 1, '70221': 2, })
        self.assertEqual(len(resp_json['information_data']), 18)
        self.assertEqual(resp_json['information_data']
                         [0]['type'], 'LEC/STUDIO')
        self.assertEqual(resp_json['information_data'][0]['group'], 'LE')
        self.assertEqual(resp_json['information_data'][0]['day'], 'FRI')
        self.assertEqual(resp_json['information_data'][0]['time'], '1130-1220')
        self.assertEqual(resp_json['information_data'][0]['venue'], 'LT23')
        self.assertEqual(resp_json['information_data'][0]['remark'], '')


class CourseIndexGetCoursesTestCase(IndexSwapperBaseTestCase):
    ENDPOINT = '/indexswapper/courseindex/get_courses/'

    def test_success_default(self):
        resp = self.client3.get(self.ENDPOINT)
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp_json['count'], 3)
        self.assertEqual(resp_json['total_pages'], 1)
        self.assertEqual(len(resp_json['results']), 3)
        self.assertEqual(resp_json['results'][0]['code'], 'MH1100')
        self.assertEqual(resp_json['results'][1]['code'], 'MH1200')
        self.assertEqual(resp_json['results'][2]['code'], 'MH1300')
        self.assertEqual(resp_json['results'][0]['name'], 'CALCULUS I')
        self.assertEqual(list(resp_json.keys()),
                         ['count', 'prev', 'next', 'total_pages', 'results'])
        self.assertEqual(list(resp_json['results'][0].keys()),
                         ['code', 'name'])

    def test_success_qp_pagination(self):
        resp = self.client3.get(self.ENDPOINT, {
            'page_size': 2,
            'page': 2,
        })
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp_json['count'], 3)
        self.assertEqual(resp_json['total_pages'], 2)
        self.assertEqual(len(resp_json['results']), 1)
        self.assertEqual(resp_json['results'][0]['code'], 'MH1300')

    def test_success_pagination_next_prev(self):
        resp = self.client3.get(self.ENDPOINT, {
            'page_size': 2,
        })
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp_json['count'], 3)
        self.assertEqual(resp_json['total_pages'], 2)
        self.assertEqual(len(resp_json['results']), 2)
        self.assertEqual(
            resp_json['next'], 'http://testserver/indexswapper/courseindex/get_courses/?page=2&page_size=2')
        self.assertIsNone(resp_json['prev'])
        resp2 = self.client3.get(resp_json['next'])
        resp_json2 = loads(resp2.content.decode('utf-8'))
        self.assertEqual(resp_json2['count'], 3)
        self.assertEqual(resp_json2['total_pages'], 2)
        self.assertEqual(len(resp_json2['results']), 1)
        self.assertIsNone(resp_json2['next'])
        self.assertEqual(
            resp_json2['prev'], 'http://testserver/indexswapper/courseindex/get_courses/?page_size=2')

    def test_success_qp_ordering(self):
        resp = self.client3.get(self.ENDPOINT, {
            'page_size': 1,
            'page': 1,
            'ordering': '-name'
        })
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp_json['count'], 3)
        self.assertEqual(resp_json['total_pages'], 3)
        self.assertEqual(len(resp_json['results']), 1)
        self.assertEqual(resp_json['results'][0]['code'], 'MH1200')

    def test_success_qp_search_name(self):
        resp = self.client3.get(self.ENDPOINT, {
            'name__icontains': 'calcu',
        })
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp_json['count'], 1)
        self.assertEqual(resp_json['total_pages'], 1)
        self.assertEqual(len(resp_json['results']), 1)
        self.assertEqual(resp_json['results'][0]['code'], 'MH1100')

    def test_success_qp_search_code(self):
        resp = self.client3.get(self.ENDPOINT, {
            'code__icontains': 'MH1',
        })
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp_json['count'], 3)
        self.assertEqual(resp_json['total_pages'], 1)
        self.assertEqual(len(resp_json['results']), 3)
        self.assertEqual(resp_json['results'][0]['code'], 'MH1100')
        self.assertEqual(resp_json['results'][1]['code'], 'MH1200')
        self.assertEqual(resp_json['results'][2]['code'], 'MH1300')

    def test_success_qp_search_custom_1(self):
        resp = self.client3.get(self.ENDPOINT, {
            'search__icontains': '120',
        })
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp_json['count'], 1)
        self.assertEqual(resp_json['total_pages'], 1)
        self.assertEqual(len(resp_json['results']), 1)
        self.assertEqual(resp_json['results'][0]['code'], 'MH1200')

    def test_success_qp_search_custom_2(self):
        resp = self.client3.get(self.ENDPOINT, {
            'search__icontains': 'foundation',
        })
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp_json['count'], 1)
        self.assertEqual(resp_json['total_pages'], 1)
        self.assertEqual(len(resp_json['results']), 1)
        self.assertEqual(resp_json['results'][0]['code'], 'MH1300')


class CourseIndexGetIndexesTestCase(IndexSwapperBaseTestCase):
    ENDPOINT = (
        lambda _, course_code: f'/indexswapper/courseindex/get_indexes/{course_code}/')

    def test_fail_invalid_course(self):
        resp = self.client3.get(self.ENDPOINT('ZZ9999'))
        self.assertEqual(resp.status_code, 404)

    def test_success_default(self):
        resp = self.client3.get(self.ENDPOINT('MH1100'))
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(len(resp_json), 12)
        self.assertEqual(list(resp_json[0].keys()), [
                         'index', 'information', 'pending_count'])
        self.assertEqual(list(resp_json[0]['information'][0].keys()), [
                         'type', 'group', 'day', 'time', 'venue', 'remark'])
