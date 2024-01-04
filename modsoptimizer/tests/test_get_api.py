from sso.tests.base_test import BaseAPITestCase


class CourseCodeListAPITestCase(BaseAPITestCase):
    fixtures = ['mods_sample_course_codes.json', 'mods_sample_course_indexes.json']
    ENDPOINT = '/modsoptimizer/course_code/'
    
    def test_get_success(self):
        resp = self.client.get(self.ENDPOINT)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 12)
        self.assertEqual(resp.data['total_pages'], 2)
        
    def test_search_icontains_1(self):
        resp = self.client.get(self.ENDPOINT, {'search__icontains': 'math'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 5)
        self.assertEqual(resp.data['results'][0]['code'], 'MH1301')
        self.assertEqual(resp.data['results'][0]['name'], 'DISCRETE MATHEMATICS')
        self.assertEqual(resp.data['results'][1]['code'], 'MH1801')
        self.assertEqual(resp.data['results'][1]['name'], 'MATHEMATICS 1')
        self.assertEqual(resp.data['results'][2]['code'], 'MH1811')
        self.assertEqual(resp.data['results'][2]['name'], 'MATHEMATICS 2')
        self.assertEqual(resp.data['results'][3]['code'], 'MH1812')
        self.assertEqual(resp.data['results'][3]['name'], 'DISCRETE MATHEMATICS')
        self.assertEqual(resp.data['results'][4]['code'], 'MH2811')
        self.assertEqual(resp.data['results'][4]['name'], 'MATHEMATICS II')
        
    def test_search_icontains_1(self):
        resp = self.client.get(self.ENDPOINT, {'search__icontains': 'MH1201 lin'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['code'], 'MH1201')
        self.assertEqual(resp.data['results'][0]['name'], 'LINEAR ALGEBRA II')


class CourseIndexDetailAPITestCase(BaseAPITestCase):
    fixtures = ['mods_sample_course_codes.json', 'mods_sample_course_indexes.json']
    ENDPOINT = (lambda _, course_index: f'/modsoptimizer/course_index/{course_index}/')
    
    def test_fail_not_found(self):
        resp = self.client3.get(self.ENDPOINT('00000'))
        self.assertEqual(resp.status_code, 404)
    
    def test_get_success(self):
        resp = self.client3.get(self.ENDPOINT('70501'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['index'], '70501')


class CourseCodeDetailAPITestCase(BaseAPITestCase):
    fixtures = ['mods_sample_course_codes.json', 'mods_sample_course_indexes.json']
    ENDPOINT = (lambda _, course_code: f'/modsoptimizer/course_code/{course_code}/')
    
    def test_fail_not_found(self):
        resp = self.client3.get(self.ENDPOINT('00000'))
        self.assertEqual(resp.status_code, 404)
    
    def test_get_success(self):
        resp = self.client3.get(self.ENDPOINT('MH1101'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['code'], 'MH1101')
        self.assertEqual(resp.data['name'], 'CALCULUS II')
