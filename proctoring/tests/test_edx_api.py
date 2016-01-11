"""
Tests for Open EdX API calls
"""
import json

from mock import patch

from django.test import TestCase
from django.contrib.auth.models import User

from person.models import Student
from proctoring import edx_api
from proctoring.models import EventSession, Exam, Course
from journaling.models import Journaling


class RequestsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'test', 'test@example.com', 'testpassword'
        )
        event = EventSession()
        event.testing_center = "new center"
        event.course = Course.create_by_course_run('org/course/run')
        event.course_event_id = "new event"
        event.proctor = self.user
        event.save()
        exam1 = Exam()
        exam1.exam_code = 'examCode'
        exam1.organization = 'organization'
        exam1.duration = 1
        exam1.reviewed_exam = 'reviewedExam'
        exam1.reviewer_notes = 'reviewerNotes'
        exam1.exam_password = 'examPassword'
        exam1.exam_sponsor = 'examSponsor'
        exam1.exam_name = 'examName'
        exam1.ssi_product = 'ssiProduct'
        exam1.first_name = 'firstName'
        exam1.last_name = 'lastName'
        exam1.username = 'test'
        exam1.user_id = 1
        exam1.email = 'test@test.com'
        exam1.exam_id = event.course_event_id
        exam1.course_id = event.course_id
        exam1.event = event
        student = Student.objects.get_or_create(
            sso_id=exam1.user_id,
            email=exam1.email,
            first_name=exam1.first_name,
            last_name=exam1.last_name
        )[0]
        exam1.student = student
        exam1.save()
        exam2 = Exam()
        exam2.exam_code = 'examCode2'
        exam2.organization = 'organization'
        exam2.duration = 1
        exam2.reviewed_exam = 'reviewedExam'
        exam2.reviewer_notes = 'reviewerNotes'
        exam2.exam_password = 'examPassword'
        exam2.exam_sponsor = 'examSponsor'
        exam2.exam_name = 'examName'
        exam2.ssi_product = 'ssiProduct'
        exam2.first_name = 'firstName'
        exam2.last_name = 'lastName'
        exam2.username = 'test'
        exam2.user_id = 1
        exam2.email = 'test@test.com'
        exam2.exam_id = event.course_event_id
        exam2.course_id = event.course_id
        exam2.event = event
        exam2.student = student
        exam2.save()
        self.exams = [exam1, exam2]

    @patch('proctoring.edx_api._journaling_request')
    def test_start_exam_request(self, request):
        request.return_value = MockResponse(content={"status": "OK"})
        response = edx_api.start_exam_request('exam_code')
        self.assertTrue(request.called)
        self.assertEqual(response.content, {"status": "OK"})

    @patch('proctoring.edx_api._journaling_request')
    def test_stop_exam_request(self, request):
        request.return_value = MockResponse(content={"status": "OK"})
        response = edx_api.stop_exam_request('id', 'action', 1)
        self.assertTrue(request.called)
        self.assertEqual(response.content, {"status": "OK"})

    @patch('proctoring.edx_api.poll_status')
    def test_poll_status(self, request):
        request.return_value = MockResponse(content={"key": "value"})
        result = edx_api.poll_status_request(['code1','code2'])
        self.assertEqual(len(result), 2)

    @patch('proctoring.edx_api.poll_status')
    def test_wrong_poll_status(self, request):
        request.return_value = MockResponse(content={"key": "value"})
        result = edx_api.poll_status_request({})
        self.assertEqual(type(result), list)

    @patch('proctoring.edx_api._journaling_request')
    def test_send_review_request(self, request):
        request.return_value = MockResponse(content={"status": "OK"})
        response = edx_api.send_review_request({'key': 'value'})
        self.assertTrue(request.called)
        self.assertEqual(response.content, {"status": "OK"})

    @patch('proctoring.edx_api._journaling_request')
    def test_get_proctored_exams_request(self, request):
        request.return_value = MockResponse(content={"status": "OK"})
        response = edx_api.get_proctored_exams_request()
        self.assertTrue(request.called)
        self.assertEqual(response.content, {"status": "OK"})

    @patch('proctoring.edx_api._journaling_request')
    def test_bulk_start_exams_request(self, request):
        request.return_value = MockResponse(content={"status": "OK"})
        result = edx_api.bulk_start_exams_request(self.exams)
        self.assertTrue(request.called)
        self.assertEqual(len(result), 2)

class JournalingRequestTestCase(TestCase):
    def test_post(self):
        with patch('proctoring.edx_api.requests.post') as requests:
            requests.return_value = MockResponse(content='{"status": "OK"}')
            journaling_count = Journaling.objects.count()
            response = edx_api._journaling_request('post', 'test')
            self.assertEqual(response.content, '{"status": "OK"}')
            self.assertEqual(journaling_count + 1, Journaling.objects.count())

    def test_get(self):
        with patch('proctoring.edx_api.requests.get') as requests:
            requests.return_value = MockResponse(content="""
<html>
    <header></header>
    <body>
        <h1>Header Text</h1>
        <pre class="exception_value">Exception Value</pre>
    </body>
</html>
            """)
            response = edx_api._journaling_request('get', 'test')
            self.assertIn('Header Text', response.content)
            self.assertIn('Exception Value', response.content)

    def test_put(self):
        with patch('proctoring.edx_api.requests.put') as requests:
            requests.return_value = MockResponse(content="Just a text")
            response = edx_api._journaling_request('put', 'test')
            self.assertEqual('Just a text', response.content)


class MockResponse(object):
    def __init__(self, status_code=200, content={"status": "OK"}):
        self.status_code = status_code
        self.content = content

    def json(self):
        if isinstance(self.content, dict):
            result = self.content
        else:
            try:
                result = json.loads(self.content)
            except ValueError:
                result = {}
        return result
