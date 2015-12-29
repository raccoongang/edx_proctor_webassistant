import json
from datetime import datetime
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status

from django.contrib.auth.models import User
from django.test import TestCase

from journaling import api_views
from journaling.models import Journaling
from person.models import Permission
from proctoring.tests.test_models import _create_exam


class JournalingTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'test',
            'test@test.com',
            'password'
        )
        Permission.objects.create(
            user=self.user,
            object_type="*",
            object_id="*",
            role=Permission.ROLE_PROCTOR
        )
        exam = _create_exam('test', 'org1/course1/run1')
        Journaling.objects.create(
            journaling_type=Journaling.EVENT_SESSION_START,
            event_id=1,
            exam=exam,
            proctor=self.user,
            note='test note',
        )

    def test_list(self):
        factory = APIRequestFactory()
        request = factory.get(
            '/api/journaling/')
        force_authenticate(request, user=self.user)
        view = api_views.JournalingViewSet.as_view({'get': 'list'})
        response = view(request)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(type(data), dict)
        self.assertEqual(len(data.get('results')), Journaling.objects.count())

        # test filters
        request = factory.get(
            '/api/journaling/?proctor=%s&exam_code=%s&type=%s&'
            'date=%s' % (
                'test',
                'examCode_test',
                Journaling.EVENT_SESSION_START,
                datetime.now().date()

            ))
        force_authenticate(request, user=self.user)
        view = api_views.JournalingViewSet.as_view({'get': 'list'})
        response = view(request)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(type(data), dict)
        self.assertEqual(len(data.get('results')), Journaling.objects.count())

        # test filter by hash key and wrong date
        request = factory.get(
            '/api/journaling/?event_hash=%s&date=%s' % (
                'test',
                'wrong_date'
            ))
        force_authenticate(request, user=self.user)
        view = api_views.JournalingViewSet.as_view({'get': 'list'})
        response = view(request)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data.get('results')), 0)
