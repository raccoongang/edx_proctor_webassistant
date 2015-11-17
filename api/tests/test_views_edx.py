import json
from datetime import datetime
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory
from api.models import Exam, EventSession
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
        exam.exam_code = 'examCode'
        exam.organization = 'organization'
        exam.duration = 1
        exam.reviewed_exam = 'reviewedExam'
        exam.reviewer_notes = 'reviewerNotes'
        exam.exam_password = 'examPassword'
        exam.exam_sponsor = 'examSponsor'
        exam.exam_name = 'examName'
        exam.ssi_product = 'ssiProduct'
        exam.first_name = 'firstName'
        exam.last_name = 'lastName'
        exam.exam_id = '1'
        exam.course_id = 'org1/course1/run1'
        exam.save()
        self.exam = exam
        self.event = EventSession()
        self.event.testing_center = 'testing center'
        self.event.course_id = exam.course_id
        self.event.course_event_id = exam.exam_id
        self.event.status = EventSession.IN_PROGRESS
        self.event.proctor = User.objects.create_user(
            'test',
            'test@test.com',
            'password'
        )
        self.event.save()

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
            'examCode': self.exam.exam_code,
            'duration': self.exam.duration,
            'reviewedExam': self.exam.reviewed_exam,
            'reviewerNotes': self.exam.reviewer_notes,
            'examPassword': self.exam.exam_password,
            'examSponsor': self.exam.exam_sponsor,
            'examName': self.exam.exam_name,
            'ssiProduct': self.exam.ssi_product,
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
                "examID": "wrong_exam",
                "courseID": "wrong/course/id",
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
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

            exam_data['orgExtra'] = '''{
                "examStartDate": "2015-10-10 11:00",
                "examEndDate": "2015-10-10 15:00",
                "noOfStudents": 1,
                "examID": "1",
                "courseID": "org1/course1/run1",
                "firstName": "first_name",
                "lastName": "last_name"
            }'''
            request = factory.post(
                '/api/exam_register/',
                data=exam_data,
            )
            view = ExamViewSet.as_view({'post': 'create'})
            response = view(request)
            response.render()
            data = json.loads(response.content)
            self.assertEqual(type(data), dict)
            exam = Exam.objects.get(exam_code=exam_data['examCode'])
            self.assertDictContainsSubset({
                "examCode": exam.exam_code,
                "duration ": exam.duration,
                "organization ": exam.organization,
                "reviewedExam ": exam.reviewed_exam,
                "reviewerNotes ": exam.reviewer_notes,
                "examPassword ": exam.exam_password,
                "examSponsor ": exam.exam_sponsor,
                "examName ": exam.exam_name,
                "ssiProduct ": exam.ssi_product,
            },
                exam_data
            )
            self.assertListEqual(
                ["org1", "org1/course1", "org1/course1/run1"],
                [exam.course_organization, exam.course_identify,
                 exam.course_run]
            )
            self.assertEqual(data['ID'], self.event.hash_key)
            self.assertEqual(Exam.objects.count(), 2)
