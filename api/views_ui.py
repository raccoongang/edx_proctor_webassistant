import json
from datetime import datetime
from rest_framework.decorators import api_view, authentication_classes, \
    permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.settings import api_settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, status, mixins
from rest_framework.authentication import BasicAuthentication, \
    TokenAuthentication
from api.web_soket_methods import send_ws_msg
from models import Exam, EventSession
from serializers import EventSessionSerializer
from edx_api import (start_exam_request, stop_exam_request, poll_status_request,
                     send_review_request, get_proctored_exams,
                     bulk_start_exams_request,
                     bulk_send_review_request)
from api.auth import CsrfExemptSessionAuthentication, SsoTokenAuthentication


@api_view(['GET'])
@authentication_classes((SsoTokenAuthentication,))
@permission_classes((IsAuthenticated,))
def start_exam(request, attempt_code):
    exam = get_object_or_404(Exam, exam_code=attempt_code)

    response = start_exam_request(exam.exam_code)
    if response.status_code == 200:
        exam.exam_status = exam.STARTED
        exam.proctor = request.user
        exam.attempt_status = "OK"
        exam.save()
        data = {
            'hash': exam.generate_key(),
            'proctor': exam.proctor.username,
            'status': "OK"
        }
        send_ws_msg(data, channel=exam.event.hash_key)
    else:
        data = {'error': 'Edx response error. See logs'}
    return Response(data=data, status=response.status_code)


@api_view(['PUT'])
@authentication_classes((SsoTokenAuthentication, CsrfExemptSessionAuthentication))
@permission_classes((IsAuthenticated,))
def stop_exam(request, pk):
    response = stop_exam_request(pk)
    return Response(status=response.status_code)


@api_view(['POST'])
@authentication_classes((SsoTokenAuthentication, CsrfExemptSessionAuthentication))
@permission_classes((IsAuthenticated,))
def poll_status(request):
    data = request.data
    print(data)
    if u'list' in data:
        response = poll_status_request(data['list'])
        for val in response:
            exam = get_object_or_404(Exam, exam_code=val['attempt_code'])
            print(exam)
            exam.attempt_status = val.get('status')
            exam.save()
            data = {
                'hash': exam.generate_key(),
                'status': exam.attempt_status
            }
            send_ws_msg(data, channel=exam.event.hash_key)
        return Response(status=status.HTTP_200_OK)
    else:
        print("'list' not in data")
        return Response(status=status.HTTP_400_BAD_REQUEST)


class EventSessionViewSet(mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):
    """
    Event managment API

    For **create** send `testing_center`,`course_id`,`course_event_id`
    Other fields filling automaticaly

    You can **update** only `status` and `notify` fields
    """
    serializer_class = EventSessionSerializer
    queryset = EventSession.objects.all()
    authentication_classes = (
        SsoTokenAuthentication, CsrfExemptSessionAuthentication,
        BasicAuthentication)

    def create(self, request, *args, **kwargs):
        fields_for_create = ['testing_center', 'course_id', 'course_event_id']
        data = {}
        for field in fields_for_create:
            data[field] = request.data.get(field)
        # Return existing session if match test_center, ourse_id and exam_id
        # so the proctor is able to connect to existing session
        data['status'] = EventSession.IN_PROGRESS
        sessions = EventSession.objects.filter(**data).order_by('-start_date')
        if sessions:
            session = sessions[0]
            serializer = EventSessionSerializer(session)
            return Response(serializer.data,
                            status=status.HTTP_200_OK,
                            headers=self.get_success_headers(serializer.data))
        # else create session
        data['proctor'] = request.user.pk
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def get_success_headers(self, data):
        try:
            return {'Location': data[api_settings.URL_FIELD_NAME]}
        except (TypeError, KeyError):
            return {}

    def partial_update(self, request, *args, **kwargs):

        instance = self.get_object()
        fields_for_update = ['status', 'notify']
        data = {}

        for field in fields_for_update:
            data[field] = request.data.get(field)
        change_end_date = instance.status == EventSession.IN_PROGRESS and \
                          data.get('status') == EventSession.FINISHED

        serializer = self.get_serializer(instance, data=data,
                                         partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if change_end_date:
            event_session = EventSession.objects.get(pk=instance.pk)
            event_session.end_date = datetime.now()
            event_session.save()
            serializer = self.get_serializer(event_session)
        return Response(serializer.data)


class Review(APIView):
    authentication_classes = (
        SsoTokenAuthentication, CsrfExemptSessionAuthentication,
        BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        Request example:

        ```
        {
                "examMetaData": {
                    "examCode": "C27DE6D1-39D6-4147-8BE0-9E9440D4A971"
                },
                 "reviewStatus": "Clean",
                 "videoReviewLink": "http://video.url",
                 "desktopComments": [ ]
            }
        ```

        """
        passing_review_status = ['Clean', 'Rules Violation']
        failing_review_status = ['Not Reviewed', 'Suspicious']
        payload = request.data
        required_fields = ['examMetaData', 'reviewStatus',
                           'videoReviewLink', 'desktopComments']
        for field in required_fields:
            if field not in payload:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        exam = get_object_or_404(
            Exam,
            exam_code=payload['examMetaData']['examCode']
        )

        payload['examMetaData'].update(
            {
                "ssiRecordLocator": exam.generate_key(),
                "reviewerNotes": ""
            }
        )

        response = send_review_request(payload)

        return Response(
            status=response.status_code
        )


class BulkReview(APIView):
    authentication_classes = (
        SsoTokenAuthentication, CsrfExemptSessionAuthentication,
        BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        Request example:

        ````
        [
            {
                "examMetaData": {
                    "examCode": "C27DE6D1-39D6-4147-8BE0-9E9440D4A971",
                    "ssiRecordLocator": "5649f201ab718b6610285f81",
                    "reviewedExam": true,
                    "reviewerNotes": "Everything is ok"
                },
                 "reviewStatus": "Clean",
                 "videoReviewLink": "http://video.url",
                 "desktopComments": [
                    {
                        "comments": "Browsing other websites",
                        "duration": 88,
                        "eventFinish": 88,
                        "eventStart": 12,
                        "eventStatus": "Suspicious"
                    }
                 ]
            },
            {...}
        ]
        ```

        """
        review_payload_list = []
        exams = request.data
        for exam in exams:
            try:
                exam_obj = Exam.objects.get(
                    exam_code=exam.get('examMetaData', {}).get('examCode')
                )
            except Exam.DoesNotExist:
                continue

            review_payload_list.append(_review_payload(
                exam_obj,
                exam_obj.exam_code,
                exam.get('reviewStatus', {}),
                exam.get('videoReviewLink', {}),
                exam.get('desktopComments', {})
            ))

        data = bulk_send_review_request(review_payload_list)
        return Response(data=data, status=200)


@api_view(['GET'])
@authentication_classes((SsoTokenAuthentication,))
@permission_classes((IsAuthenticated,))
def get_exams_proctored(request):
    response = get_proctored_exams()
    return Response(
        status=response.status_code,
        data=response.json()
    )


@api_view(['POST'])
@authentication_classes((SsoTokenAuthentication, CsrfExemptSessionAuthentication))
@permission_classes((IsAuthenticated,))
def bulk_start_exams(request):
    """
    Start list of exams by exam codes.

    :param request:
    :param exam_codes: comaseparated list of exam codes
    :return:
    """

    exam_codes = request.data.get('list', [])
    exam_list = Exam.objects.filter(exam_code__in=exam_codes)
    items = bulk_start_exams_request(exam_list)
    for exam in items:
        exam.exam_status = exam.STARTED
        exam.proctor = request.user
        exam.save()
        data = {
            'hash': exam.generate_key(),
            'proctor': exam.proctor.username,
            'status': "OK"
        }
        send_ws_msg(data, channel=exam.event.hash_key)
    return Response(status=status.HTTP_200_OK)


def _review_payload(exam, exam_code, review_status, video_link,
                    desktop_comments):
    return {
        "examDate": "",
        "examProcessingStatus": "Review Completed",
        "examTakerEmail": " ",
        "examTakerFirstName": exam.first_name,
        "examTakerLastName": exam.last_name,
        "keySetVersion": "",
        "examApiData": {
            "duration": exam.duration,
            "examCode": exam.exam_code,
            "examName": exam.exam_name,
            "examPassword": exam.exam_password,
            "examSponsor": exam.exam_sponsor,
            "examUrl": "http://localhost:8000/api/edx_proctoring/proctoring_launch_callback/start_exam/4d07a01a-1502-422e-b943-93ac04dc6ced",
            "orgExtra": {
                "courseID": exam.course_id,
                "examEndDate": exam.exam_end_date,
                "examID": exam.exam_id,
                "examStartDate": exam.exam_start_date,
                "noOfStudents": exam.no_of_students
            },
            "organization": exam.organization,
            "reviewedExam": exam.reviewed_exam,
            "reviewerNotes": exam.reviewer_notes,
            "ssiProduct": "rp-now"
        },
        "overAllComments": "",
        "reviewStatus": review_status,
        "userPhotoBase64String": "",
        "videoReviewLink": video_link,
        "examMetaData": {
            "examCode": exam_code,
            "examName": exam.exam_name,
            "examSponsor": exam.exam_sponsor,
            "organization": exam.organization,
            "reviewedExam": "True",
            "reviewerNotes": "Closed Book",
            "simulatedExam": "False",
            "ssiExamToken": "",
            "ssiProduct": "rp-now",
            "ssiRecordLocator": exam.generate_key()
        },
        "desktopComments": desktop_comments,
        "webCamComments": [
            {
                "comments": "Photo ID not provided",
                "duration": 796,
                "eventFinish": 796,
                "eventStart": 0,
                "eventStatus": "Suspicious"
            }
        ]
    }
