import json

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status

from django.contrib.auth.models import User
from django.test import TestCase

from person.models import Permission
from person import api_views


class PermissionTestCase(TestCase):
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

    def test_list(self):
        factory = APIRequestFactory()
        request = factory.get(
            '/api/permission/')
        force_authenticate(request, user=self.user)
        view = api_views.PermissionViewSet.as_view({'get': 'list'})
        response = view(request)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(type(data), dict)
        self.assertDictContainsSubset(
            data,
            {
                "role": "proctor",
                "instructor": [],
                "proctor": [{"object_type": "*", "object_id": "*"}]
            }
        )
