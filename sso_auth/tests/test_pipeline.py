"""
Tests for SSO Auth Pypelines
"""
from mock import patch

from django.test import TestCase
from django.contrib.auth.models import User

from person.models import Permission
from sso_auth.pipeline import (set_roles_for_edx_users,
                               create_or_update_permissions, update_user_name)


class PipelineTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'test1', 'test1@test.com', 'testpassword'
        )
        self.permissions = [
            {
                'obj_perm': [u'Proctoring'],
                'obj_type': Permission.TYPE_ORG,
                'obj_id': "*",
            },
            {
                'obj_perm': [u'*'],
                'obj_type': Permission.TYPE_COURSE,
                'obj_id': 'org2/course1',
            },
            {
                'obj_perm': [u'Wrong'],
                'obj_type': Permission.TYPE_ORG,
                'obj_id': 'org1',
            }
        ]

    def test_set_roles_for_edx_users(self):
        perms_count = self.user.permission_set.count()
        set_roles_for_edx_users(self.user, self.permissions)
        self.assertEqual(perms_count + 2, self.user.permission_set.count())
        new_permissions = [
            {
                'obj_perm': [u'Proctoring'],
                'obj_type': Permission.TYPE_ORG,
                'obj_id': "*",
            }
        ]
        set_roles_for_edx_users(self.user, new_permissions)
        self.assertEqual(self.user.permission_set.count(), 1)

    @patch('sso_auth.pipeline.log')
    def test_create_or_update_permissions(self, mock_logging):
        perms_count = self.user.permission_set.count()
        response = {
            'permissions': [{
                'obj_perm': [u'Proctoring'],
                'obj_type': Permission.TYPE_COURSERUN,
                'obj_id': "org1/course2/run1",
            }]
        }
        result = create_or_update_permissions('', self.user, response,
                                              self.user, response)
        self.assertEqual(type(result), dict)
        self.assertEqual(perms_count + 1, self.user.permission_set.count())

        # send wrong data
        response = {
            'permissions': [{}]
        }
        create_or_update_permissions('', self.user, response,
                                     self.user, response)
        self.assertTrue(mock_logging.error.called)

    def test_update_username(self):
        response = {
            'email': 'test1@test.com',
            'firstname': 'FirstName',
            'lastname': 'LastName'
        }
        update_user_name(backend='', user=self.user, response=response,
                         strategy='', pipeline_index='')
        user = User.objects.get(pk=self.user.pk)
        self.assertEqual(user.first_name, 'FirstName')
        self.assertEqual(user.last_name, 'LastName')

        response = {
            'email': 'non@exist.com'
        }
        result = update_user_name(backend='', user=self.user,
                                  response=response,
                                  strategy='', pipeline_index='')
        self.assertEqual(result, {})
