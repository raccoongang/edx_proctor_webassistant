from rest_framework.reverse import reverse
from rest_framework import viewsets, status, mixins
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.translation import ugettext_lazy as _
from api.web_soket_methods import send_ws_msg
from serializers import ExamSerializer
from models import Exam, EventSession


class APIRoot(APIView):
    """API Root for accounts module"""

    def get(self, request):
        result = {
            "exam_register": reverse('exam-register-list', request=request),
            "start_exam": reverse(
                'start_exam',
                request=request, args=('attempt_code',)
            ),
            "poll_status": reverse(
                'poll_status',
                request=request, args=('attempt_code',)
            ),
            "review": reverse(
                'review',
                request=request
            ),
            "event_session": reverse('event-session-list', request=request),
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
            "lastName": "last_name"
        }

    """
    serializer_class = ExamSerializer
    queryset = Exam.objects.all()

    # @csrf_exempt
    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        # try:
        #     event = EventSession.objects.get(
        #         course_id=serializer.validated_data.get('course_id'),
        #         course_event_id=serializer.validated_data.get('exam_id'),
        #         status=EventSession.IN_PROGRESS
        #     )
        #     data['hash'] = event.hash_key
        # except EventSession.DoesNotExist:
        #     return Response({'error': _("No event was found. Forbidden")},
        #                     status=status.HTTP_403_FORBIDDEN)

        self.perform_create(serializer)
        data['hash'] = serializer.instance.generate_key()
        send_ws_msg(data)
        headers = self.get_success_headers(serializer.data)
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
