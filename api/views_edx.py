from django.contrib.auth.models import User
from rest_framework.reverse import reverse
from rest_framework import viewsets, status, mixins
from rest_framework.generics import get_object_or_404
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.translation import ugettext_lazy as _
from api.web_soket_methods import send_ws_msg
from journaling.models import Journaling
from serializers import ExamSerializer
from models import Exam, EventSession


class APIRoot(APIView):
    """API Root for accounts module"""

    def get(self, request):
        result = {
            "exam_register": reverse('exam-register-list', request=request),
            "bulk_start_exams": reverse(
                'bulk_start_exams',
                request=request
            ),
            "start_exam": reverse(
                'start_exam',
                request=request, args=('-attempt_code-',)
            ),
            "poll_status": reverse(
                'poll_status',
                request=request
            ),
            "review": reverse(
                'review',
                request=request
            ),
            "proctored_exams": reverse(
                'proctor_exams',
                request=request
            ),
            "journaling": reverse(
                'journaling-list',
                request=request
            ),
            "event_session": reverse('event-session-list', request=request),
            "archived_event_session": reverse('archived-event-session-list',
                                              request=request),
        }
        return Response(result)


class ExamViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    """
    This viewset register edx's exam on proctoring service and return generated code
    Required parameters:
    ```
    examCode,
    organization,
    duration,
    reviewedExam,
    reviewerNotes,
    examPassword,
    examSponsor,
    examName,
    ssiProduct,
    orgExtra
    ```

    orgExtra contain json like this:

        {
            "examStartDate": "2015-10-10 11:00",
            "examEndDate": "2015-10-10 15:00",
            "noOfStudents": 1,
            "examID": "id",
            "courseID": "edx_org/edx_course/edx_courserun",
            "firstName": "first_name",
            "lastName": "last_name",
            "userID": "1",
            "email": "test@test.com",
            "username": "test"
        }

    """

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
                event = EventSession.objects.get(
                    hash_key=hash_key,
                    status=EventSession.IN_PROGRESS
                )
                return Exam.objects.filter(
                    event=event
                )
            except EventSession.DoesNotExist:
                return Exam.objects.filter(pk__lt=0)
        else:
            return []

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        event = EventSession.objects.filter(
            course_id=serializer.validated_data.get('course_id'),
            course_event_id=serializer.validated_data.get('exam_id'),
            status=EventSession.IN_PROGRESS
        ).order_by('start_date')
        if len(event) == 0:
            return Response(
                {'error': _("No event was found. Forbidden")},
                status=status.HTTP_403_FORBIDDEN)
        elif len(event) > 1:
            event = event.reverse()[0]
        else:
            event = event[0]
        self.perform_create(serializer)
        data['hash'] = serializer.instance.generate_key()
        send_ws_msg(data, channel=event.hash_key)
        headers = self.get_success_headers(serializer.data)
        serializer.instance.event = event
        serializer.instance.save()
        Journaling.objects.create(
            type=Journaling.EXAM_ATTEMPT,
            event=event,
            exam=serializer.instance,
        )
        return Response({'ID': data['hash']},
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': data[api_settings.URL_FIELD_NAME]}
        except (TypeError, KeyError):
            return {}
