import json
from datetime import datetime
from mock import patch

from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from django.contrib.auth.models import User
from django.test import TestCase

from proctoring.models import Exam, EventSession, ArchivedEventSession, \
    Comment, Course, InProgressEventSession
from person.models import Permission, Student
from proctoring import api_ui_views


class ViewsUITestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'test', 'test@example.com', 'testpassword'
        )
        Permission.objects.create(
            user=self.user,
            object_id='*',
            object_type='*'
        )
        event = EventSession()
        event.testing_center = "new center"
        event.course = Course.create_by_course_run('org/course/run')
        event.course_event_id = "new event"
        event.proctor = self.user
        event.save()
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
        exam.username = 'test'
        exam.user_id = 1
        exam.email = 'test@test.com'
        exam.exam_id = event.course_event_id
        exam.course_id = event.course_id
        exam.event = event
        student = Student.objects.get_or_create(
            sso_id=exam.user_id,
            email=exam.email,
            first_name=exam.first_name,
            last_name=exam.last_name
        )[0]
        exam.student = student
        exam.save()
        self.exam = exam

    def test_get_status(self):
        with patch("proctoring.api_ui_views.poll_status") as poll_status:
            poll_status.return_value = EdxResponse({"status": "bar"})
            self.assertEqual(api_ui_views._get_status("foo"), 'bar')

    @patch('proctoring.api_ui_views.send_ws_msg')
    def test_start_exam(self, send_ws_msg):
        factory = APIRequestFactory()
        with patch(
            'proctoring.api_ui_views.start_exam_request') as edx_request:
            edx_request.return_value = MockResponse()
            request = factory.get(
                '/api/start_exam/%s' % self.exam.exam_code)
            force_authenticate(request, user=self.user)
            response = api_ui_views.StartExam.as_view()(
                request,
                self.exam.exam_code
            )
            response.render()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = json.loads(response.content)
            self.assertIn('hash', data)
            self.assertIn('status', data)

    def test_wrong_start_exam(self):
        factory = APIRequestFactory()
        with patch(
            'proctoring.api_ui_views.start_exam_request') as edx_request:
            edx_request.return_value = MockResponse(
                status_code=status.HTTP_400_BAD_REQUEST
            )
            request = factory.get(
                '/api/start_exam/%s' % self.exam.exam_code)
            force_authenticate(request, user=self.user)
            response = api_ui_views.StartExam.as_view()(
                request,
                self.exam.exam_code
            )
            response.render()
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            data = json.loads(response.content)
            self.assertIn('error', data)

    @patch('proctoring.api_ui_views.send_ws_msg')
    def test_stop_exam(self, send_ws_msg):
        factory = APIRequestFactory()
        with patch('proctoring.api_ui_views.stop_exam_request') as edx_request:
            edx_request.return_value = MockResponse(
                status_code=status.HTTP_200_OK
            )
            request = factory.put('/api/stop_exam/%s' % self.exam.exam_code)
            force_authenticate(request, user=self.user)
            response = api_ui_views.StopExam.as_view()(
                request,
                self.exam.exam_code
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            response.render()
            data = {
                'action': 'action',
                'user_id': self.exam.user_id
            }
            request = factory.put('/api/stop_exam/%s' % self.exam.exam_code,
                                  data=data)
            force_authenticate(request, user=self.user)
            response = api_ui_views.StopExam.as_view()(
                request,
                self.exam.exam_code
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response.render()
            data = json.loads(response.content)
            self.assertDictContainsSubset({
                'hash': self.exam.generate_key(),
            },
                data
            )

    @patch('proctoring.api_ui_views.send_ws_msg')
    def test_stop_exams(self, send_ws_msg):
        factory = APIRequestFactory()
        wrong_data = {
            "attempts":
                """[{
                    "attempt_code": "%s"
                }]""" % self.exam.exam_code
        }
        data = {
            "attempts":
                """[{
                    "attempt_code": "%s",
                    "action": "action",
                    "user_id": %s
                }]""" % (self.exam.exam_code, self.exam.user_id),
        }
        request = factory.put('/api/stop_exams/')
        force_authenticate(request, user=self.user)
        response = api_ui_views.StopExams.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        request = factory.put('/api/stop_exams/', wrong_data)
        force_authenticate(request, user=self.user)
        response = api_ui_views.StopExams.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        with patch('proctoring.api_ui_views.stop_exam_request') as edx_request:
            edx_request.return_value = MockResponse(
                status_code=status.HTTP_400_BAD_REQUEST
            )
            request = factory.put('/api/stop_exams/', data=data)
            force_authenticate(request, user=self.user)
            response = api_ui_views.StopExams.as_view()(request)
            self.assertEqual(response.status_code,
                             status.HTTP_500_INTERNAL_SERVER_ERROR)
        with patch('proctoring.api_ui_views.stop_exam_request') as edx_request:
            edx_request.return_value = MockResponse(
                status_code=status.HTTP_200_OK
            )
            request = factory.put('/api/stop_exams/', data=data)
            force_authenticate(request, user=self.user)
            response = api_ui_views.StopExams.as_view()(request)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('proctoring.api_ui_views.send_ws_msg')
    def test_poll_status(self, send_ws_msg):
        factory = APIRequestFactory()
        data = {'list': [self.exam.exam_code]}
        self.exam.attempt_status = 'ready_to_start'
        self.exam.save()
        actual_start_date = self.exam.actual_start_date
        actual_end_date = self.exam.actual_end_date
        # send bed request
        request = factory.post('/api/poll_status', {})
        force_authenticate(request, user=self.user)
        response = api_ui_views.PollStatus.as_view()(request)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # change status on started
        with patch(
            'proctoring.api_ui_views.poll_status_request') as edx_request:
            edx_request.return_value = [
                {"attempt_code": self.exam.exam_code, "status": "started"}]
            request = factory.post(
                '/api/poll_status', data)
            force_authenticate(request, user=self.user)
            response = api_ui_views.PollStatus.as_view()(request)
            response.render()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            exam = Exam.objects.get(pk=self.exam.pk)
            self.assertNotEqual(actual_start_date, exam.actual_start_date)

        data = {'list': [self.exam.exam_code]}

        # change status on submitted
        with patch(
            'proctoring.api_ui_views.poll_status_request') as edx_request:
            edx_request.return_value = [
                {"attempt_code": self.exam.exam_code, "status": "submitted"}]
            request = factory.post(
                '/api/poll_status', data)
            force_authenticate(request, user=self.user)
            response = api_ui_views.PollStatus.as_view()(request)
            response.render()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            exam = Exam.objects.get(pk=self.exam.pk)
            self.assertNotEqual(actual_end_date, exam.actual_end_date)

    def test_send_review(self):
        factory = APIRequestFactory()
        comment_count = Comment.objects.count()
        with patch(
            'proctoring.api_ui_views.send_review_request') as edx_request:
            edx_request.return_value = MockResponse()
            data = {
                "desktopComments": """[
                        {
                            "comments": "Browsing other websites",
                            "duration": 88,
                            "eventFinish": 88,
                            "eventStart": 12,
                            "eventStatus": "Suspicious"
                        }
                    ]""",
                "examMetaData": '{"examCode": "%s"}' % self.exam.exam_code,
                "reviewStatus": "Clean",
                "videoReviewLink": "http://video.url",
            }
            request = factory.post(
                '/api/review/', data=data)
            force_authenticate(request, user=self.user)
            view = api_ui_views.Review.as_view()
            response = view(request)
            response.render()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(comment_count + 1, Comment.objects.count())

    def test_send_wrong_review(self):
        factory = APIRequestFactory()
        with patch(
            'proctoring.api_ui_views.send_review_request') as edx_request:
            edx_request.return_value = MockResponse(status_code=400)
            request = factory.post(
                '/api/review/', data={'attempt_code': self.exam.exam_code})
            force_authenticate(request, user=self.user)
            view = api_ui_views.Review.as_view()
            response = view(request)
            response.render()
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class GetExamsProctoredTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'test', 'test@example.com', 'testpassword'
        )
        Permission.objects.create(
            user=self.user,
            object_id='*',
            object_type='*'
        )

    def test_get(self):
        factory = APIRequestFactory()
        with patch(
            'proctoring.api_ui_views.get_proctored_exams_request') as exams:
            exams.return_value = MockResponse(status_code=200, content="""{
                "results": [
                    {
                        "id": "org/course/id",

                        "proctored_exams": ["exam"]
                    }
                ]
            }""")
            request = factory.get('/api/proctored_exams/')
            force_authenticate(request, user=self.user)
            view = api_ui_views.GetExamsProctored.as_view()
            response = view(request)
            response.render()
            data = json.loads(response.content)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(type(data), dict)
            self.assertDictContainsSubset({
                "id": "org/course/id",
                "proctored_exams": ['exam'],
                "has_access": True
            },data['results'][0])


class EventSessionViewSetTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'test', 'test@example.com', 'testpassword'
        )
        Permission.objects.create(
            user=self.user,
            object_type="*",
            object_id="*"
        )

    def test_create_event(self):
        factory = APIRequestFactory()
        event_data = {
            'testing_center': u'test_center',
            'course_id': u'test/course/id',
            'course_event_id': u'test course event',
            "course_name": "Display Course Name"

        }
        request = factory.post(
            '/api/event_session/', data=event_data)
        force_authenticate(request, user=self.user)
        view = api_ui_views.EventSessionViewSet.as_view({'post': 'create'})
        response = view(request)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = json.loads(response.content)
        self.assertEqual(type(data), dict)
        event = EventSession.objects.get(pk=data['id'])
        self.assertDictContainsSubset({
            "testing_center": event.testing_center,
            "course_id": event.course.get_full_course(),
            "course_event_id": event.course_event_id,
        },
            event_data
        )
        self.assertEqual(event.course.course_name, "Display Course Name")

        # Try to create event wich already exists
        request = factory.post(
            '/api/event_session/', data=event_data)
        force_authenticate(request, user=self.user)
        view = api_ui_views.EventSessionViewSet.as_view({'post': 'create'})
        response = view(request)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(type(data), dict)
        event = EventSession.objects.get(pk=data['id'])
        self.assertDictContainsSubset({
            "testing_center": event.testing_center,
            "course_id": event.course.get_full_course(),
            "course_event_id": event.course_event_id,
        },
            event_data
        )

    @patch('proctoring.api_ui_views.send_ws_msg')
    def test_update_event(self, send_ws_msg):
        event = EventSession()
        event.testing_center = "new center"
        event.course = Course.create_by_course_run("new/course/id")
        event.course_event_id = "new event"
        event.proctor = self.user
        event.save()
        self.assertEqual(event.end_date, None)
        factory = APIRequestFactory()
        event_data = {
            'status': EventSession.ARCHIVED,
            'notify': 'new notify',
            'comment': 'new comment'
        }
        request = factory.patch(
            '/api/event_session/%s' % event.pk, data=event_data)
        force_authenticate(request, user=self.user)
        view = api_ui_views.EventSessionViewSet.as_view(
            {'patch': 'partial_update'})
        response = view(request, pk=event.pk)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(type(data), dict)
        event = ArchivedEventSession.objects.get(pk=data['id'])
        self.assertDictContainsSubset({
            "status": event.status,
            "notify": event.notify,
        },
            event_data
        )
        self.assertNotEqual(event.end_date, None)

    def test_list(self):
        event = InProgressEventSession()
        event.testing_center = "another center"
        event.course = Course.create_by_course_run("another/course/id")
        event.course_event_id = "another event"
        event.proctor = self.user
        event.save()
        event = InProgressEventSession.objects.get(pk=event.pk)
        factory = APIRequestFactory()
        request = factory.get(
            '/api/event_session/')
        force_authenticate(request, user=self.user)
        view = api_ui_views.EventSessionViewSet.as_view({'get': 'list'})
        response = view(request)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(type(data), list)
        self.assertEqual(len(data), InProgressEventSession.objects.count())

        # test filters by hash key
        request = factory.get(
            '/api/event_session/?session=%s' % event.hash_key
        )
        force_authenticate(request, user=self.user)
        view = api_ui_views.EventSessionViewSet.as_view({'get': 'list'})
        response = view(request)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(type(data), list)
        self.assertEqual(len(data), InProgressEventSession.objects.filter(
            hash_key=event.hash_key).count())


class ArchivedEventSessionViewSetTestCase(TestCase):
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
        self.event = InProgressEventSession()
        self.event.testing_center = "new center"
        self.event.course = Course.create_by_course_run("new/course/id")
        self.event.course_event_id = "new event"
        self.event.status = EventSession.ARCHIVED
        self.event.proctor = self.user
        self.event.end_date = datetime.now().date()
        self.event.save()

    def test_list(self):
        factory = APIRequestFactory()
        request = factory.get(
            '/api/archived_exam/')
        force_authenticate(request, user=self.user)
        view = api_ui_views.ArchivedEventSessionViewSet.as_view(
            {'get': 'list'})
        response = view(request)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(type(data), dict)
        self.assertEqual(len(data.get('results')),
                         ArchivedEventSession.objects.count())

        # test filters
        request = factory.get(
            '/api/archived_exam/?'
            'testing_center=%s'
            '&proctor=%s'
            '&hash_key=%s'
            '&course_id=%s'
            '&course_event_id=%s'
            '&start_date=%s'
            '&end_date=%s'
            % (
                'new center',
                'test',
                self.event.hash_key,
                self.event.course.get_full_course(),
                self.event.course_event_id,
                datetime.now().date(),
                datetime.now().date()
            ))
        force_authenticate(request, user=self.user)
        view = api_ui_views.ArchivedEventSessionViewSet.as_view(
            {'get': 'list'})
        response = view(request)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(type(data), dict)
        self.assertEqual(len(data.get('results')),
                         ArchivedEventSession.objects.count())

        # test filter by first name, last name, key and wrong date
        request = factory.get(
            '/api/archived_exam/?'
            '&proctor=%s'
            '&course_id=%s'
            '&start_date=%s'
            '&end_date=%s'
            % (
                'new user',
                'non/exist/course',
                'wrong_date',
                'wrong_date',
            ))
        force_authenticate(request, user=self.user)
        view = api_ui_views.ArchivedEventSessionViewSet.as_view(
            {'get': 'list'})
        response = view(request)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data.get('results')), 0)


class MockResponse(object):
    def __init__(self, status_code=200, content={"status": "OK"}):
        self.status_code = status_code
        self.content = content


class EdxResponse(object):
    def __init__(self, json_string):
        self.json_string = json_string

    def json(self):
        return self.json_string
