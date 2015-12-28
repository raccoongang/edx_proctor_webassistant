# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets, status, mixins
from rest_framework.authentication import BasicAuthentication
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from edx_proctor_webassistant.auth import CsrfExemptSessionAuthentication
from edx_proctor_webassistant.web_soket_methods import send_ws_msg
from journaling.models import Journaling
from models import Exam, InProgressEventSession, Course
from serializers import ExamSerializer


class APIRoot(APIView):
    """API Root with list of available endpoints"""

    def get(self, request):
        result = {
            "exam_register": reverse('exam-register-list', request=request),
            "bulk_start_exams": reverse('bulk_start_exams', request=request),
            "start_exam": reverse('start_exam', request=request,
                                   args=('-attempt_code-',)),
            "stop_exam": reverse('stop_exam', request=request,
                                   args=('-attempt_code-',)),
            "bulk_start_exams": reverse('bulk_start_exams', request=request),
            "stop_exams": reverse('stop_exams', request=request),
            "poll_status": reverse('poll_status', request=request),
            "review": reverse('review', request=request),
            "proctored_exams": reverse('proctor_exams', request=request),
            "journaling": reverse('journaling-list', request=request),
            "event_session": reverse('event-session-list', request=request),
            "archived_event_session": reverse('archived-event-session-list',
                                               request=request),
            "archived_exam": reverse('archived-exam-list', request=request),
            "permission": reverse('permission-list', request=request),
            "comment": reverse('comment-list', request=request),

        }
        return Response(result)


class ExamViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    """
    This viewset register edx's exam on proctoring service and return
    generated code

    Required parameters:

        `examCode`,
        `organization`,
        `duration`,
        `reviewedExam`,
        `reviewerNotes`,
        `examPassword`,
        `examSponsor`,
        `examName`,
        `ssiProduct`,
        `orgExtra`

    orgExtra contain json like this:

        {
            "examStartDate": "2015-10-10 11:00",
            "examEndDate": "2015-10-10 15:00",
            "noOfStudents": 1,
            "examID": "id",
            "courseID": "course-v1:edX+DemoX+Demo_Course",
            "firstName": "first_name",
            "lastName": "last_name",
            "userID": "1",
            "email": "test@test.com",
            "username": "test"
        }

    """
    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)
    serializer_class = ExamSerializer
    queryset = Exam.objects.all()

    def get_queryset(self):
        """
        This view should return a list of all the purchases for
        the user as determined by the username portion of the URL.
        """
        hash_key = self.request.query_params.get('session')
        if hash_key is not None and hash_key:
            try:
                event = InProgressEventSession.objects.get(
                    hash_key=hash_key,
                )
                return Exam.objects.by_user_perms(self.request.user).filter(
                    event=event
                )
            except InProgressEventSession.DoesNotExist:
                return Exam.objects.filter(pk__lt=0)
        else:
            return []

    def create(self, request, *args, **kwargs):
        """
        Create new exam, on exam attempt.
        Find Event Session for this exam.
        """
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        event = InProgressEventSession.objects.filter(
            course=serializer.validated_data.get('course'),
            course_event_id=serializer.validated_data.get('exam_id'),
        ).order_by('-start_date')
        if not event:
            return _send_journaling_response(
                request=request,
                data=data,
                result={'error': _("No event was found. Forbidden")},
                status_code=status.HTTP_403_FORBIDDEN
            )
        event = event[0]
        self.perform_create(serializer)
        data['hash'] = serializer.instance.generate_key()
        data['status'] = 'created'
        send_ws_msg(data, channel=event.hash_key)
        headers = self.get_success_headers(serializer.data)
        serializer.instance.event = event
        serializer.instance.save()
        Journaling.objects.create(
            journaling_type=Journaling.EXAM_ATTEMPT,
            event=event,
            exam=serializer.instance,
        )
        return _send_journaling_response(
            request=request,
            data=data,
            result={'ID': data['hash']},
            status_code=status.HTTP_201_CREATED,
            headers=headers
        )


def _send_journaling_response(request, data, result, status_code,
                              headers=None):
    """
    Journaling all requests and responses from edX
    """
    Journaling.objects.create(
        journaling_type=Journaling.API_REQUESTS,
        note="""
Requested url:%s
Sent data: %s
Response status: %s
Response content: %s
            """ % (
            reverse('exam-register-list', request=request),
            str(data), status_code, str(result))
    )
    return Response(result,
                    status=status_code,
                    headers=headers)
