from rest_framework import status
from rest_framework.reverse import reverse
from json import loads
from portal.models import FeedbackForm
from sso.tests.base_test import BaseAPITestCase


class PortalUpdate(BaseAPITestCase):
    @classmethod
    def setUpTestData(self):
        super().setUpTestData()
        self.feedback1 = FeedbackForm.objects.create(
            type=FeedbackForm.Type.BUG_REPORT,
            title='UFacility Booking Bug',
            details='it shows error when booking'
        )
        self.feedback2 = FeedbackForm.objects.create(
            type=FeedbackForm.Type.FEATURE_REQUEST,
            title='Make Index Swapper',
            details='plz make this app!!',
            email='some_email@e.ntu.edu.sg'
        )
    
    def test_feedback_list(self):
        # regular user should not be able to get all feedbacks
        resp1 = self.client2.get(
            reverse('portal:feedback')
        )
        self.assertEqual(resp1.status_code, status.HTTP_403_FORBIDDEN)
        
        # admin should get a list of all feedbacks
        resp2 = self.client1.get(
            reverse('portal:feedback'), {}
        )
        resp_json2 = loads(resp2.content.decode('utf-8'))
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp_json2), 2)
        self.assertEqual(resp_json2[0]['resolved'], False)
        self.assertEqual(resp_json2[0]['title'], 'UFacility Booking Bug')
    
    def test_feedback_user_post_invalid(self):
        # title cannot be empty
        resp1 = self.client3.post(
            reverse('portal:feedback'),
            {
                'type': 'BR',
                'title': '',
                'details': 'some detail',
            }
        )
        resp_json1 = loads(resp1.content.decode('utf-8'))
        self.assertEqual(resp1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp_json1['title'][0], 'This field may not be blank.')
        
        # invalid type given
        resp2 = self.client3.post(
            reverse('portal:feedback'),
            {
                'type': 'XX',
                'title': 'some title',
                'details': 'some detail',
            }
        )
        resp_json2 = loads(resp2.content.decode('utf-8'))
        self.assertEqual(resp2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp_json2['type'][0], '"XX" is not a valid choice.')

    def test_feedback_user_post_valid(self):
        # valid feedback given
        resp = self.client3.post(
            reverse('portal:feedback'),
            {
                'type': 'IR',
                'title': 'some title',
                'details': 'some detail',
                'email': '',
            }
        )
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp_json['title'], 'some title')
        self.assertEqual(FeedbackForm.objects.all().count(), 3)

    def test_feedback_detail_unauthorized(self):
        # feedback detail can only be seen by superuser
        resp = self.client2.get(
            reverse('portal:feedback_detail', args=(1,))
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_feedback_detail_valid(self):
        # test detail view for feedbacks by superuser
        resp = self.client1.get(
            reverse('portal:feedback_detail', args=(2,))
        )
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_json['title'], 'Make Index Swapper')
    
    def test_feedback_admin_post_unauthorized(self):
        # only admin can send feedback
        resp = self.client2.put(
            reverse('portal:feedback_detail', args=(1,)), {
                'response': 'some response'
            }
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_feedback_admin_post_valid(self):
        # valid response by admin
        resp1 = self.client1.put(
            reverse('portal:feedback_detail', args=(1,)), {
                'response': 'some response'
            }
        )
        self.assertEqual(resp1.status_code, status.HTTP_200_OK)
        feedback = FeedbackForm.objects.get(id=1)
        self.assertTrue(feedback.resolved)
        self.assertEqual(feedback.response, 'some response')

        # cannot send response if issue already resolved
        resp2 = self.client1.put(
            reverse('portal:feedback_detail', args=(1,)), {
                'response': 'some response 2'
            }
        )
        resp_json = loads(resp2.content.decode('utf-8'))
        self.assertEqual(resp2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsInstance(resp_json[0], str)
