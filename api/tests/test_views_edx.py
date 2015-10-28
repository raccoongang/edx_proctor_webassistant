import json
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory
from api.models import Exam
from api.views_edx import APIRoot, ExamViewSet
from mock import patch


class APIRootTestCase(TestCase):
    def test_get(self):
        factory = APIRequestFactory()
        request = factory.get('/api/')
        view = APIRoot.as_view()
        response = view(request)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(type(data), dict)


class ExamViewSetTestCase(TestCase):
    def setUp(self):
        exam = Exam()
        exam.examCode = 'examCode'
        exam.organization = 'organization'
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

    def test_get_list_exams(self):
        factory = APIRequestFactory()
        request = factory.get('/api/exam_register/')
        view = ExamViewSet.as_view({'get': 'list'})
        response = view(request)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(type(data), list)
        self.assertEqual(len(data), Exam.objects.count())

    def test_get_exam(self):
        factory = APIRequestFactory()
        request = factory.get(
            '/api/exam_register/%s' % self.exam.pk)
        view = ExamViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=self.exam.pk)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(type(data), dict)
        self.assertDictContainsSubset({
            'examCode': self.exam.examCode,
            'duration': self.exam.duration,
            'reviewedExam': self.exam.reviewedExam,
            'reviewerNotes': self.exam.reviewerNotes,
            'examPassword': self.exam.examPassword,
            'examSponsor': self.exam.examSponsor,
            'examName': self.exam.examName,
            'ssiProduct': self.exam.ssiProduct,
        },
            data)

    def test_register_exam(self):
        factory = APIRequestFactory()
        exam_data = {
            "examCode": "newEamCode",
            "duration ": 2,
            "organization ": "newOrganization",
            "reviewedExam ": "newReviewedExam",
            "reviewerNotes ": "newReviewerNotes",
            "examPassword ": "newExamPassword",
            "examSponsor ": "newExamSponsor",
            "examName ": "newExamName",
            "ssiProduct ": "newSsiProduct",
            "orgExtra": '''{
                "examStartDate": "2015-10-10 11:00",
                "examEndDate": "2015-10-10 15:00",
                "noOfStudents": 1,
                "examId": "id",
                "courseId": "org1/course1/run1",
                "firstName": "first_name",
                "lastName": "last_name"
            }'''
        }
        with patch('api.views_edx.send_ws_msg') as send_ws:
            send_ws.return_value = None
            request = factory.post('/api/exam_register/',
                                   data=exam_data,
                                   )
            view = ExamViewSet.as_view({'post': 'create'})
            response = view(request)
            response.render()
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            data = json.loads(response.content)
            self.assertEqual(type(data), dict)
            exam = Exam.objects.get(examCode=exam_data['examCode'])
            self.assertDictContainsSubset({
                "examCode": exam.examCode,
                "duration ": exam.duration,
                "organization ": exam.organization,
                "reviewedExam ": exam.reviewedExam,
                "reviewerNotes ": exam.reviewerNotes,
                "examPassword ": exam.examPassword,
                "examSponsor ": exam.examSponsor,
                "examName ": exam.examName,
                "ssiProduct ": exam.ssiProduct,
            },
                exam_data
            )
            self.assertListEqual(
                ["org1", "org1/course1", "org1/course1/run1"],
                [exam.course_organization, exam.course_identify,
                 exam.course_run]
            )
            self.assertEqual(Exam.objects.count(), 2)
