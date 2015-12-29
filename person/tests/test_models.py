from django.contrib.auth.models import User
from django.test import TestCase
from person.models import Permission


class PermissionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'test',
            'test@test.com',
            'password'
        )
        self.permission = Permission.objects.create(
            user=self.user,
            object_type=Permission.TYPE_COURSE,
            object_id='course_org/course_id/course_run',
            role=Permission.ROLE_PROCTOR
        )

    def test_get_exam_field_by_type(self):
        result = self.permission._get_exam_field_by_type()
        self.assertEqual(type(result), str)

    def test_prepare_object_id(self):
        result = self.permission.prepare_object_id()
        self.assertEqual(type(result), str)
        self.assertEqual(result, 'course_org/course_id')

    def test_course_run_to_course(self):
        result = Permission._course_run_to_course('a/b/c')
        self.assertEqual(type(result), str)
        self.assertEqual(result, 'a/b')
        result = Permission._course_run_to_course('abc')
        self.assertEqual(type(result), str)
        self.assertEqual(result, 'abc')
