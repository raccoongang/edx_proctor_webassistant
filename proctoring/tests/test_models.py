from django.test import TestCase
from django.contrib.auth.models import User
from person.models import Permission
from proctoring.models import Exam, Course


class HasPermissionToCourseTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'test1', 'test1@test.com', 'testpassword'
        )


class ExamByUserPermsManagerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'test1', 'test1@test.com', 'testpassword'
        )
        exam1 = _create_exam(1, 'org1/course1/run1')
        exam2 = _create_exam(2, 'org1/course2/run1')
        exam3 = _create_exam(3, 'org1/course2/run2')
        exam4 = _create_exam(4, 'org2/course1/run1')

    def test_by_user_perms(self):
        exams = Exam.objects.by_user_perms(self.user)
        self.assertEqual(len(exams), 0)
        perm1 = Permission.objects.create(
            user=self.user,
            object_id='org2/course1/run1',
            object_type=Permission.TYPE_COURSERUN
        )
        exams = Exam.objects.by_user_perms(self.user)
        self.assertEqual(len(exams), 1)
        self.assertEqual(exams[0].course_run, 'org2/course1/run1')
        perm2 = Permission.objects.create(
            user=self.user,
            object_id='org1/course2/run1',
            object_type=Permission.TYPE_COURSERUN
        )
        exams = Exam.objects.by_user_perms(self.user)
        self.assertEqual(len(exams), 2)
        perm1.delete()
        perm3 = Permission.objects.create(
            user=self.user,
            object_id='org1/course2',
            object_type=Permission.TYPE_COURSE
        )
        exams = Exam.objects.by_user_perms(self.user)
        self.assertEqual(len(exams), 2)
        perm2.delete()
        perm3.delete()
        perm4 = Permission.objects.create(
            user=self.user,
            object_id='org1',
            object_type=Permission.TYPE_ORG
        )
        exams = Exam.objects.by_user_perms(self.user)
        self.assertEqual(len(exams), 3)
        perm4.delete()
        perm5 = Permission.objects.create(
            user=self.user,
            object_id='*',
            object_type=Permission.TYPE_ORG
        )
        exams = Exam.objects.by_user_perms(self.user)
        self.assertEqual(len(exams), 4)


class ExamTestCase(TestCase):
    def setUp(self):
        self.exam = _create_exam(1)

    def test_generate_key(self):
        result = self.exam.generate_key()
        self.assertEqual(type(result), str)
        self.assertRegexpMatches(result, r"([a-fA-F\d]{32})")


def _create_exam(id, course_id):
    exam = Exam()
    exam.exam_code = 'examCode_%s' % id
    exam.duration = 1
    exam.reviewed_exam = 'reviewedExam_%s' % id
    exam.reviewer_notes = 'reviewerNotes_%s' % id
    exam.exam_password = 'examPassword_%s' % id
    exam.exam_sponsor = 'examSponsor_%s' % id
    exam.exam_name = 'examName_%s' % id
    exam.ssi_product = 'ssiProduct_%s' % id
    exam.first_name = 'firstName_%s' % id
    exam.last_name = 'lastName_%s' % id,
    exam.course = Course.create_by_course_run(course_id)
    exam.exam_id = '1'
    exam.email = 'test@test.com'
    exam.student_id = '1'
    exam.save()
    return exam
