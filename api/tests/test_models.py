from django.test import TestCase
from api.models import Exam


class ExamTestCase(TestCase):
    def setUp(self):
        exam = Exam()
        exam.examCode = 'examCode'
        exam.duration = 1
        exam.reviewedExam = 'reviewedExam'
        exam.reviewerNotes = 'reviewerNotes'
        exam.examPassword = 'examPassword'
        exam.examSponsor = 'examSponsor'
        exam.examName = 'examName'
        exam.ssiProduct = 'ssiProduct'
        exam.firstName = 'firstName'
        exam.lastName = 'lastName'
        exam.examId = '1'
        exam.save()
        self.exam = exam

    def test_generate_key(self):
        result = self.exam.generate_key()
        self.assertEqual(type(result), str)
        self.assertRegexpMatches(result, r"([a-fA-F\d]{32})")
