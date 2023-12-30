from sso.tests.base_test import BaseAPITestCase


class CourseCodeListAPITestCase(BaseAPITestCase):
    fixtures = ['mods_sample_course_codes.json', 'mods_sample_course_indexes.json']
    ENDPOINT = '/modsoptimizer/course_code/'

    def test_get_success(self):
        resp = self.client.get(self.ENDPOINT)
        self.assertEqual(resp.status_code, 200)
        # TODO later
