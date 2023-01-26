from rest_framework import status
from rest_framework.reverse import reverse
from json import loads
from portal.models import UpdateNote
from sso.tests.base_test import BaseAPITestCase


class PortalUpdate(BaseAPITestCase):
    @classmethod
    def setUpTestData(self):
        super().setUpTestData()
        self.update1 = UpdateNote.objects.create(
            title='title1',
            description='description1',
            content='<p><b>content1</b></p>',
            public=True,
        )
        self.update2 = UpdateNote.objects.create(
            title='title2',
            description='description2',
            content='<p><b>content2</b></p>',
            public=True,
        )
        # by default public=False, public should not able to retrieve this
        # used to draft update note without reveraling it directly
        self.update3 = UpdateNote.objects.create(
            title='title3',
            description='description3',
            content='<p><b>content3</b></p>',
        )
    
    def test_update_list(self):
        # get all updates in time reverse order
        resp = self.client3.get(
            reverse('portal:update')
        )
        resp_json = loads(resp.content.decode('utf-8'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp_json), 2)
        self.assertNotIn('content', resp_json[0])
        self.assertEqual(resp_json[1]['description'], 'description2')
        self.assertEqual(resp_json[0]['id'], 1)

    def test_update_post_unauthorized(self):
        # anonymous user & regular user cannot post update
        resp1 = self.client2.post(
            reverse('portal:update'),
            {
                'title': 'some_title',
                'description': 'some_description',
                'content': 'some_content',
            }
        )
        self.assertEqual(resp1.status_code, status.HTTP_403_FORBIDDEN)
        resp2 = self.client3.post(
            reverse('portal:update'),
            {
                'title': 'some_title',
                'description': 'some_description',
                'content': 'some_content',
            }
        )
        self.assertEqual(resp2.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_post_invalid(self):
        # invalid post request (title empty)
        resp1 = self.client1.post(
            reverse('portal:update'),
            {
                'title': '',
                'description': 'some_description',
                'content': 'some_content',
            }
        )
        resp_json1 = loads(resp1.content.decode('utf-8'))
        self.assertEqual(resp1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual('This field may not be blank.', resp_json1['title'][0])

    def test_update_post_valid(self):
        # valid post request, create new update
        resp1 = self.client1.post(
            reverse('portal:update'),
            {
                'title': 'some_title',
                'description': 'some_description',
                'content': 'some_content',
            }
        )
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UpdateNote.objects.all().count(), 4)
        
        # newest update will show up first
        resp2 = self.client3.get(
            reverse('portal:update')
        )
        resp_json2 = loads(resp2.content.decode('utf-8'))
        self.assertEqual(resp_json2[0]['title'], 'title1')
    
    def test_update_detail(self):
        # invalid id given
        resp1 = self.client1.get(
            reverse('portal:update_detail', args=(9,))
        )
        self.assertEqual(resp1.status_code, status.HTTP_404_NOT_FOUND)

        # valid id but not open for public
        resp1b = self.client1.get(
            reverse('portal:update_detail', args=(3,))
        )
        self.assertEqual(resp1b.status_code, status.HTTP_404_NOT_FOUND)

        # get a specific update including its content
        resp2 = self.client3.get(
            reverse('portal:update_detail', args=(1,))
        )
        resp_json = loads(resp2.content.decode('utf-8'))
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_json['title'], 'title1')
        self.assertEqual(resp_json['content'], '<p><b>content1</b></p>')

    def test_update_edit_delete_unauthorized(self):
        # put, patch, delete only accessible by superuser and not regular user
        resp1 = self.client2.put(
            reverse('portal:update_detail', args=(1,))
        )
        self.assertEqual(resp1.status_code, status.HTTP_403_FORBIDDEN)
        resp2 = self.client2.patch(
            reverse('portal:update_detail', args=(2,))
        )
        self.assertEqual(resp2.status_code, status.HTTP_403_FORBIDDEN)
        resp3 = self.client2.delete(
            reverse('portal:update_detail', args=(1,))
        )
        self.assertEqual(resp3.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_edit_valid(self):
        # valid edit (put)
        resp1 = self.client1.put(
            reverse('portal:update_detail', args=(1,)),
            {
                'title': 'edit_title',
                'description': 'edit_description',
                'content': 'edit_content',
            }
        )
        self.assertEqual(resp1.status_code, status.HTTP_200_OK)
        self.assertEqual(UpdateNote.objects.get(id=1).title, 'edit_title')
        self.assertEqual(UpdateNote.objects.get(id=1).content, 'edit_content')
        
        # valid partial update (patch)
        resp2 = self.client1.patch(
            reverse('portal:update_detail', args=(2,)),
            {
                'content': 'edit_content_only',
            }
        )
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertEqual(UpdateNote.objects.get(id=2).title, 'title2')
        self.assertEqual(UpdateNote.objects.get(id=2).content, 'edit_content_only')

    def test_update_delete(self):
        # valid delete
        resp = self.client1.delete(
            reverse('portal:update_detail', args=(2,))
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(UpdateNote.objects.all().count(), 2)
    
    def test_update_get_prev_and_next_id(self):
        # create another sample update that is open to public
        # so we have: 1 (public), 2 (public), 3 (private), 4 (public)
        self.update4 = UpdateNote.objects.create(
            title='title3',
            description='description3',
            content='<p><b>content3</b></p>',
            public=True,
        )

        resp1 = self.client3.get(
            reverse('portal:update_detail', args=(2,))
        )
        resp_json1 = loads(resp1.content.decode('utf-8'))
        self.assertEqual(resp_json1['has_prev'], 1)
        self.assertEqual(resp_json1['has_next'], 4)

        resp2 = self.client3.get(
            reverse('portal:update_detail', args=(4,))
        )
        resp_json2 = loads(resp2.content.decode('utf-8'))
        self.assertEqual(resp_json2['has_prev'], 2)
        self.assertEqual(resp_json2['has_next'], None)
