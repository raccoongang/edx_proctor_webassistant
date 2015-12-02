import json
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from api.models import Exam, Permission, EventSession
from api.views_ui import start_exam, poll_status, Review, EventSessionViewSet
from mock import patch


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
        event.course_id = "new course"
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
        exam.save()
        self.exam = exam

    def test_start_exam(self):
        factory = APIRequestFactory()
        with patch('api.views_ui.start_exam_request') as edx_request, \
                patch('api.views_ui.send_ws_msg') as send_ws:
            edx_request.return_value = MockResponse()
            send_ws.return_value = None
            request = factory.get(
                '/api/start_exam/%s' % self.exam.exam_code)
            force_authenticate(request, user=self.user)
            response = start_exam(request, attempt_code=self.exam.exam_code)
            response.render()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = json.loads(response.content)
            self.assertIn('hash', data)
            self.assertIn('status', data)

    def test_wrong_start_exam(self):
        factory = APIRequestFactory()
        with patch('api.views_ui.start_exam_request') as edx_request:
            edx_request.return_value = MockResponse(
                status_code=status.HTTP_400_BAD_REQUEST
            )
            request = factory.get(
                '/api/start_exam/%s' % self.exam.exam_code)
            force_authenticate(request, user=self.user)
            response = start_exam(request, attempt_code=self.exam.exam_code)
            response.render()
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            data = json.loads(response.content)
            self.assertIn('error', data)

    def test_poll_status(self):
        factory = APIRequestFactory()
        data = {'list': [self.exam.exam_code]}
        with patch('api.views_ui.poll_status_request') as edx_request, \
                patch('api.views_ui.send_ws_msg') as send_ws:
            edx_request.return_value = [
                {"attempt_code": self.exam.exam_code, "status": "started"}]
            send_ws.return_value = None
            request = factory.post(
                '/api/poll_status', data)
            force_authenticate(request, user=self.user)
            response = poll_status(request)
            response.render()
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_send_review(self):
        factory = APIRequestFactory()
        with patch('api.views_ui.send_review_request') as edx_request:
            edx_request.return_value = MockResponse()
            request = factory.post(
                '/api/review/', data={'attempt_code': self.exam.exam_code})
            force_authenticate(request, user=self.user)
            view = Review.as_view()
            response = view(request)
            response.render()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = json.loads(response.content)
            self.assertEqual('review_was_sent', data['status'])

    def test_send_wrong_review(self):
        factory = APIRequestFactory()
        with patch('api.views_ui.send_review_request') as edx_request:
            edx_request.return_value = MockResponse(status_code=400)
            request = factory.post(
                '/api/review/', data={'attempt_code': self.exam.exam_code})
            force_authenticate(request, user=self.user)
            view = Review.as_view()
            response = view(request)
            response.render()
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EventSessionViewSetTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'test', 'test@example.com', 'testpassword'
        )

    def test_create_event(self):
        factory = APIRequestFactory()
        event_data = {
            'testing_center': u'test_center',
            'course_id': u'test course',
            'course_event_id': u'test course event'
        }
        request = factory.post(
            '/api/event_session/', data=event_data)
        force_authenticate(request, user=self.user)
        view = EventSessionViewSet.as_view({'post': 'create'})
        response = view(request)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = json.loads(response.content)
        self.assertEqual(type(data), dict)
        event = EventSession.objects.get(pk=data['id'])
        self.assertDictContainsSubset({
            "testing_center": event.testing_center,
            "course_id": event.course_id,
            "course_event_id": event.course_event_id,
        },
            event_data
        )

    def test_update_event(self):
        event = EventSession()
        event.testing_center = "new center"
        event.course_id = "new course"
        event.course_event_id = "new event"
        event.proctor = self.user
        event.save()
        self.assertEqual(event.end_date, None)
        factory = APIRequestFactory()
        event_data = {
            'status': EventSession.FINISHED,
            'notify': 'new notify',
        }
        request = factory.patch(
            '/api/event_session/%s' % event.pk, data=event_data)
        force_authenticate(request, user=self.user)
        view = EventSessionViewSet.as_view({'patch': 'partial_update'})
        response = view(request, pk=event.pk)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(type(data), dict)
        event = EventSession.objects.get(pk=data['id'])
        self.assertDictContainsSubset({
            "status": event.status,
            "notify": event.notify,
        },
            event_data
        )
        self.assertNotEqual(event.end_date, None)


class MockResponse(object):
    def __init__(self, status_code=200, content={"status": "OK"}):
        self.status_code = status_code
        self.content = content
