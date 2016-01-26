# -*- coding: utf-8 -*-
import json
from datetime import datetime, timedelta

from django.shortcuts import redirect
from rest_framework.decorators import api_view, authentication_classes, \
    permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.settings import api_settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, status, mixins
from rest_framework.authentication import BasicAuthentication
from api.web_soket_methods import send_ws_msg
from models import Exam, EventSession, ArchivedEventSession, Comment, \
    Permission, InProgressEventSession, has_permisssion_to_course
from serializers import (EventSessionSerializer, CommentSerializer,
                         ArchivedEventSessionSerializer, JournalingSerializer,
                         ArchivedExamSerializer, PermissionSerializer)
from journaling.models import Journaling
from edx_api import (start_exam_request, stop_exam_request,
                     poll_status_request, poll_status,
                     send_review_request, get_proctored_exams_request,
                     bulk_start_exams_request,
                     bulk_send_review_request)
from api.auth import CsrfExemptSessionAuthentication, SsoTokenAuthentication, \
    IsProctor, IsInstructor, IsProctorOrInstructor
from api.utils import catch_exception


def _get_status(code):
    try:
        res = poll_status(code)
        ret_data = res.json()
        return ret_data['status']
    except:
        pass


@api_view(['GET'])
@authentication_classes((SsoTokenAuthentication,))
@permission_classes((IsAuthenticated, IsProctor))
def start_exam(request, attempt_code):
    exam = get_object_or_404(
        Exam.objects.by_user_perms(request.user),
        exam_code=attempt_code
    )
    response = start_exam_request(exam.exam_code)
    if response.status_code == 200:
        exam.exam_status = exam.STARTED
        exam.proctor = request.user
        exam.attempt_status = "OK"
        exam.save()
        Journaling.objects.create(
            type=Journaling.EXAM_STATUS_CHANGE,
            event=exam.event,
            exam=exam,
            proctor=request.user,
            note="%s -> %s" % (exam.NEW, exam.STARTED)
        )
        data = {
            'hash': exam.generate_key(),
            'proctor': exam.proctor.username,
            'status': "OK"
        }
        send_ws_msg(data, channel=exam.event.hash_key)
    else:
        data = {'error': 'Edx response error. See logs'}
    return Response(data=data, status=response.status_code)


def _stop_attempt(code, action, user_id):
    max_retries = 3
    attempt = 0
    response = stop_exam_request(code, action, user_id)
    current_status = _get_status(code)
    while attempt < max_retries \
            and current_status != 'submitted':
        response = stop_exam_request(code, action, user_id)
        current_status = _get_status(code)
        attempt += 1
    return response, current_status


@api_view(['PUT'])
@authentication_classes(
    (SsoTokenAuthentication, CsrfExemptSessionAuthentication))
@permission_classes((IsAuthenticated, IsProctor))
def stop_exam(request, attempt_code):
    """
    Endpoint for exam stops. Attempt code sends in url.
    POST parameters:
        {
            'hash': "hash_key",
            'status': "submitted"
        }

    :param request:
    :param attempt_code:
    :return:
    """
    exam = get_object_or_404(
        Exam.objects.by_user_perms(request.user),
        exam_code=attempt_code
    )
    action = request.data.get('action')
    user_id = request.data.get('user_id')
    if action and user_id:
        response, current_status = _stop_attempt(attempt_code, action, user_id)
        data = {
            'hash': exam.generate_key(),
            'status': current_status
        }
        send_ws_msg(data, channel=exam.event.hash_key)
        return Response(status=response.status_code, data=data)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@authentication_classes(
    (SsoTokenAuthentication, CsrfExemptSessionAuthentication))
@permission_classes((IsAuthenticated, IsProctor))
def stop_exams(request):
    attempts = request.data.get('attempts')
    if isinstance(attempts, basestring):
        attempts = json.loads(attempts)
    if attempts:
        status_list = []
        for attempt in attempts:
            exam = get_object_or_404(
                Exam.objects.by_user_perms(request.user),
                exam_code=attempt['attempt_code']
            )
            user_id = attempt.get('user_id')
            action = attempt.get('action')
            if action and user_id:
                response, current_status = _stop_attempt(
                    attempt['attempt_code'], action, user_id
                )
                if response.status_code != 200:
                    status_list.append(response.status_code)
                else:
                    data = {
                        'hash': exam.generate_key(),
                        'status': current_status
                    }
                    send_ws_msg(data, channel=exam.event.hash_key)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        if status_list:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes(
    (SsoTokenAuthentication, CsrfExemptSessionAuthentication))
@permission_classes((IsAuthenticated, IsProctor))
def poll_status(request):
    """
    Get statuses for list of exams

    Request example:

    ```
    {"list":["code1","code2"]}
    ```
    """
    data = request.data
    if u'list' in data:
        response = poll_status_request(data['list'])
        for val in response:
            exam = get_object_or_404(
                Exam.objects.by_user_perms(request.user),
                exam_code=val['attempt_code']
            )
            new_status = val['status']
            if (exam.attempt_status == 'ready_to_start'
                    and new_status == 'started'):
                exam.actual_start_date = datetime.now()
            if (exam.attempt_status == 'started'
                    and new_status == 'submitted')\
                or (exam.attempt_status == 'ready_to_submit'
                    and new_status == 'submitted'):
                exam.actual_end_date = datetime.now()
            exam.attempt_status = new_status
            exam.save()
            data = {
                'hash': exam.generate_key(),
                'status': exam.attempt_status
            }
            send_ws_msg(data, channel=exam.event.hash_key)
        return Response(status=status.HTTP_200_OK)
    else:
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
    queryset = InProgressEventSession.objects.all()
    authentication_classes = (
        SsoTokenAuthentication, CsrfExemptSessionAuthentication,
        BasicAuthentication)
    permission_classes = (IsAuthenticated, IsProctor)

    def get_queryset(self):
        """
        This method should return a list of all the sessions or
        list with one session for any hash_key.
        """
        hash_key = self.request.query_params.get('session')
        if hash_key:
            queryset = InProgressEventSession.objects.filter(hash_key=hash_key)
            queryset = InProgressEventSession.update_queryset_with_permissions(
                queryset, self.request.user
            )
        else:
            queryset = InProgressEventSession.objects.all()
        return queryset

    def create(self, request, *args, **kwargs):
        fields_for_create = [
            'testing_center',
            'course_id',
            'course_event_id',
            'course_name',
            'exam_name'
        ]
        data = {}
        for field in fields_for_create:
            data[field] = request.data.get(field)
        # Return existing session if match test_center, ourse_id and exam_id
        # so the proctor is able to connect to existing session
        data['status'] = EventSession.IN_PROGRESS
        sessions = InProgressEventSession.objects.filter(**data).order_by(
            '-start_date')
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
        Journaling.objects.create(
            type=Journaling.EVENT_SESSION_START,
            event=serializer.instance,
            proctor=request.user,
        )
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
        fields_for_update = ['status', 'notify', 'comment']
        data = {}

        for field in fields_for_update:
            data[field] = request.data.get(field)
        change_end_date = instance.status == EventSession.IN_PROGRESS and \
                          data.get('status') == EventSession.ARCHIVED
        if instance.status != data.get('status'):
            Journaling.objects.create(
                type=Journaling.EVENT_SESSION_STATUS_CHANGE,
                event=instance,
                proctor=request.user,
                note=instance.status + " -> " + data.get('status')
            )
        serializer = self.get_serializer(instance, data=data,
                                         partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if change_end_date:
            event_session = ArchivedEventSession.objects.get(pk=instance.pk)
            event_session.end_date = datetime.now()
            event_session.save()
            serializer = self.get_serializer(event_session)
            ws_data = {
                'end_session': change_end_date
            }
            send_ws_msg(ws_data, channel=instance.hash_key)

        return Response(serializer.data)


class ArchivedEventSessionViewSet(mixins.ListModelMixin,
                                  viewsets.GenericViewSet):
    """
    Return list of Archived Event session with pagiantion.

    You can filter results by `testing_center`, `proctor`, `hash_key`,
    `course_id`, `course_event_id`, `start_date`, `end_date`

    Add GET parameter in end of URL, for example:
    `?start_date=2015-12-04&proctor=proctor_username`
    """
    serializer_class = ArchivedEventSessionSerializer
    queryset = ArchivedEventSession.objects.all()
    paginate_by = 25
    authentication_classes = (
        SsoTokenAuthentication, CsrfExemptSessionAuthentication,
        BasicAuthentication)
    permission_classes = (IsAuthenticated, IsProctorOrInstructor)

    def get_queryset(self):

        queryset = ArchivedEventSession.objects.order_by('-pk').all()

        queryset = EventSession.update_queryset_with_permissions(
            queryset,
            self.request.user
        )

        for field, value in self.request.query_params.items():
            if field == "testing_center":
                queryset = queryset.filter(testing_center=value)
            if field == "proctor":
                try:
                    first_name, last_name = value.split(" ")
                    queryset = queryset.filter(proctor__first_name=first_name,
                                               proctor__last_name=last_name)
                except ValueError:
                    queryset = queryset.filter(proctor__username=value)
            if field == "hash_key":
                queryset = queryset.filter(hash_key=value)
            if field == "course_id":
                queryset = queryset.filter(course_id=value)
            if field == "course_event_id":
                queryset = queryset.filter(course_event_id=value)
            if field == "start_date" and len(value.split("-")) == 3:
                query_date = datetime.strptime(value, "%Y-%m-%d")
                queryset = queryset.filter(
                    start_date__gte=query_date,
                    start_date__lt=query_date + timedelta(days=1)
                )
            if field == "end_date" and len(value.split("-")) == 3:
                query_date = datetime.strptime(value, "%Y-%m-%d")
                queryset = queryset.filter(
                    end_date__gte=query_date,
                    end_date__lt=query_date + timedelta(days=1)
                )
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class Review(APIView):
    """
    POST Request example:

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
    authentication_classes = (
        SsoTokenAuthentication, CsrfExemptSessionAuthentication,
        BasicAuthentication)
    permission_classes = (IsAuthenticated, IsProctor)

    # EDX can ignore review post save procedure
    # that will result in `Pending` status for student
    # so we need to send review few times
    max_resend_attempts = 3

    @catch_exception
    def post(self, request):
        """
        Passing review statuses:  `Clean`, `Rules Violation`

        Failing review status: `Not Reviewed`, `Suspicious`
        """
        payload = request.data
        required_fields = ['examMetaData', 'reviewStatus',
                           'videoReviewLink', 'desktopComments']
        for field in required_fields:
            if field not in payload:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        if isinstance(payload['examMetaData'], basestring):
            payload['examMetaData'] = json.loads(payload['examMetaData'])
        if isinstance(payload['desktopComments'], basestring):
            payload['desktopComments'] = json.loads(payload['desktopComments'])
        exam = get_object_or_404(
            Exam.objects.by_user_perms(request.user),
            exam_code=payload['examMetaData'].get('examCode', '')
        )

        payload['examMetaData'].update(
            {
                "ssiRecordLocator": exam.generate_key(),
                "reviewerNotes": ""
            }
        )

        for comment in payload['desktopComments']:
            try:
                Comment.objects.get(
                    comment=comment.get('comments'),
                    event_status=comment.get('eventStatus'),
                    exam=exam,
                    event_start=comment.get('eventStart')
                )
            except Comment.DoesNotExist:
                Comment.objects.get_or_create(
                    comment=comment.get('comments'),
                    event_status=comment.get('eventStatus'),
                    event_start=comment.get('eventStart'),
                    event_finish=comment.get('eventFinish'),
                    duration=comment.get('duration'),
                    exam=exam
                )

        response, current_status = self.send_review(payload)
        exam.attempt_status = current_status
        exam.save()

        return Response(
            status=response.status_code
        )

    @staticmethod
    def _sent(_status):
        return _status in ['verified', 'rejected']

    def send_review(self, payload):
        attempt = 0
        code = payload['examMetaData']['examCode']
        response = send_review_request(payload)
        current_status = _get_status(code)
        while attempt < self.max_resend_attempts \
                and not self._sent(current_status):
            response = send_review_request(payload)
            current_status = _get_status(code)
            attempt += 1
        return response, current_status


# class BulkReview(APIView):
#     authentication_classes = (
#         SsoTokenAuthentication, CsrfExemptSessionAuthentication,
#         BasicAuthentication)
#     permission_classes = (IsAuthenticated, IsProctor)
#
#     def post(self, request):
#         """
#         Request example:
#
#             [
#                 {
#                     "examMetaData": {
#                         "examCode": "C27DE6D1-39D6-4147-8BE0-9E9440D4A971",
#                         "ssiRecordLocator": "5649f201ab718b6610285f81",
#                         "reviewedExam": true,
#                         "reviewerNotes": "Everything is ok"
#                     },
#                      "reviewStatus": "Clean",
#                      "videoReviewLink": "http://video.url",
#                      "desktopComments": [
#                         {
#                             "comments": "Browsing other websites",
#                             "duration": 88,
#                             "eventFinish": 88,
#                             "eventStart": 12,
#                             "eventStatus": "Suspicious"
#                         }
#                      ]
#                 },
#                 {...}
#             ]
#
#         """
#         review_payload_list = []
#         exams = request.data
#         for exam in exams:
#             try:
#                 exam_obj = Exam.objects.by_user_perms(request.user).get(
#                     exam_code=exam.get('examMetaData', {}).get('examCode')
#                 )
#             except Exam.DoesNotExist:
#                 continue
#
#             review_payload_list.append(_review_payload(
#                 exam_obj,
#                 exam_obj.exam_code,
#                 exam.get('reviewStatus', {}),
#                 exam.get('videoReviewLink', {}),
#                 exam.get('desktopComments', {})
#             ))
#
#         data = bulk_send_review_request(review_payload_list)
#         return Response(data=data, status=200)


@api_view(['GET'])
@authentication_classes((SsoTokenAuthentication,))
@permission_classes((IsAuthenticated, IsProctorOrInstructor))
def get_exams_proctored(request):
    response = get_proctored_exams_request()
    content = json.loads(response.content)
    permissions = request.user.permission_set.all()
    ret = []
    for result in content.get('results', []):
        if result['proctored_exams']:
            result['has_access'] = has_permisssion_to_course(
                request.user, result.get('id'), permissions)
            ret.append(result)
    return Response(
        status=response.status_code,
        data={"results": ret}
    )


@api_view(['POST'])
@authentication_classes(
    (SsoTokenAuthentication, CsrfExemptSessionAuthentication))
@permission_classes((IsAuthenticated, IsProctor))
def bulk_start_exams(request):
    """
    Start list of exams by exam codes.

    :param request:
    :param exam_codes: comaseparated list of exam codes
    :return:
    """

    exam_codes = request.data.get('list', [])
    # exam_list = Exam.objects.by_user_perms(request.user).filter(
    #     exam_code__in=exam_codes)
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
    Journaling.objects.create(
        type=Journaling.BULK_EXAM_STATUS_CHANGE,
        note="%s. %s -> %s" % (exam_codes, Exam.NEW, Exam.STARTED),
        proctor=request.user,
    )
    return Response(status=status.HTTP_200_OK)


# def _review_payload(exam, exam_code, review_status, video_link,
#                     desktop_comments):
#     return {
#         "examDate": "",
#         "examProcessingStatus": "Review Completed",
#         "examTakerEmail": " ",
#         "examTakerFirstName": exam.first_name,
#         "examTakerLastName": exam.last_name,
#         "keySetVersion": "",
#         "examApiData": {
#             "duration": exam.duration,
#             "examCode": exam.exam_code,
#             "examName": exam.exam_name,
#             "examPassword": exam.exam_password,
#             "examSponsor": exam.exam_sponsor,
#             "examUrl": "http://localhost:8000/api/edx_proctoring/"
#                        "proctoring_launch_callback/start_exam/"
#                        "4d07a01a-1502-422e-b943-93ac04dc6ced",
#             "orgExtra": {
#                 "courseID": exam.course_id,
#                 "examEndDate": exam.exam_end_date,
#                 "examID": exam.exam_id,
#                 "examStartDate": exam.exam_start_date,
#                 "noOfStudents": exam.no_of_students
#             },
#             "organization": exam.organization,
#             "reviewedExam": exam.reviewed_exam,
#             "reviewerNotes": exam.reviewer_notes,
#             "ssiProduct": "rp-now"
#         },
#         "overAllComments": "",
#         "reviewStatus": review_status,
#         "userPhotoBase64String": "",
#         "videoReviewLink": video_link,
#         "examMetaData": {
#             "examCode": exam_code,
#             "examName": exam.exam_name,
#             "examSponsor": exam.exam_sponsor,
#             "organization": exam.organization,
#             "reviewedExam": "True",
#             "reviewerNotes": "Closed Book",
#             "simulatedExam": "False",
#             "ssiExamToken": "",
#             "ssiProduct": "rp-now",
#             "ssiRecordLocator": exam.generate_key()
#         },
#         "desktopComments": desktop_comments,
#         "webCamComments": [
#             {
#                 "comments": "Photo ID not provided",
#                 "duration": 796,
#                 "eventFinish": 796,
#                 "eventStart": 0,
#                 "eventStatus": "Suspicious"
#             }
#         ]
#     }


# Angular redirect
def redirect_ui(request):
    return redirect('/#{}'.format(request.path))


@api_view(['POST'])
@authentication_classes(
    (SsoTokenAuthentication, CsrfExemptSessionAuthentication))
@permission_classes((IsAuthenticated, IsProctor))
def comments_journaling(request):
    """
    Add proctor comments to journal
    Request example:

        {
            "examCode" : "C27DE6D1-39D6-4147-8BE0-9E9440D4A971",
            "comment" : {
                            "comments": "Browsing other websites",
                            "duration": 88,
                            "eventFinish": 88,
                            "eventStart": 12,
                            "eventStatus": "Suspicious"
                        }
        }
    """
    data = request.data
    if u'examCode' in data and u'comment' in data:
        exam = get_object_or_404(
            Exam.objects.by_user_perms(request.user),
            exam_code=data['examCode']
        )
        comment = data['comment']
        Journaling.objects.create(
            type=Journaling.EXAM_COMMENT,
            event=exam.event,
            exam=exam,
            proctor=request.user,
            note="""
                Duration: %s
                Event start: %s
                Event finish: %s
                eventStatus": %s
                Comment:
                %s
            """ % (comment.get('duration'),
                   comment.get('eventStart'),
                   comment.get('eventFinish'),
                   comment.get('eventStatus'),
                   comment.get('comments'),
                   ),
        )
        return Response(status=status.HTTP_201_CREATED)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


class JournalingViewSet(mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """
    Return list of Journaling with pagiantion.

    You can filter results by `event_hash`, `proctor`,`exam_code`,
    `type`, `date`

    Add GET parameter in end of URL, for example:

    `?date=2015-12-04&type=8`

    """
    serializer_class = JournalingSerializer
    queryset = Journaling.objects.order_by('-pk').all()
    paginate_by = 25
    authentication_classes = (
        SsoTokenAuthentication, CsrfExemptSessionAuthentication,
        BasicAuthentication)
    permission_classes = (IsAuthenticated, IsProctor)

    def get_queryset(self):
        queryset = Journaling.objects.order_by('-pk').all()
        for field, value in self.request.query_params.items():
            if field == "proctor":
                queryset = queryset.filter(proctor__username=value)
            if field == "exam_code":
                queryset = queryset.filter(exam__exam_code=value)
            if field == "type":
                queryset = queryset.filter(type=value)
            if field == "event_hash":
                queryset = queryset.filter(event__hash_key=value)
            if field == "date" and len(value.split("-")) == 3:
                query_date = datetime.strptime(value, "%Y-%m-%d")
                queryset = queryset.filter(
                    datetime__gte=query_date,
                    datetime__lt=query_date + timedelta(days=1)
                )
        return queryset


class ArchivedExamViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Return list of Archived Exams with pagiantion.

    You can filter results by `event_hash`, `courseID`, `examStartDate`,
    `examEndDate`, `username`, `email`

    Add GET parameter in end of URL, for example:
    `?examStartDate=2015-12-04&email=test@test.com`
    """
    serializer_class = ArchivedExamSerializer
    paginate_by = 50
    queryset = Exam.objects.filter(event__status=EventSession.ARCHIVED).all()
    authentication_classes = (
        SsoTokenAuthentication, CsrfExemptSessionAuthentication,
        BasicAuthentication)
    permission_classes = (IsAuthenticated, IsProctorOrInstructor)

    def get_queryset(self):

        queryset = Exam.objects.by_user_perms(
            self.request.user).filter(
            event__status=EventSession.ARCHIVED).order_by('-pk').all()
        if self.request.user.permission_set.filter(
                role=Permission.ROLE_PROCTOR).exists():
            is_super_proctor = False
            for permission in self.request.user.permission_set.filter(
                    role=Permission.ROLE_PROCTOR).all():
                if permission.object_id == "*":
                    is_super_proctor = True
                    break
            if not is_super_proctor:
                queryset = queryset.filter(
                    event__proctor=self.request.user)

        for field, value in self.request.query_params.items():
            if field == "event_hash":
                queryset = queryset.filter(event__hash_key=value)
            if field == "courseID":
                queryset = queryset.filter(course_id=value)
            if field == "username":
                queryset = queryset.filter(username=value)
            if field == "email":
                queryset = queryset.filter(email=value)
            if field == "examStartDate" and len(value.split("-")) == 3:
                query_date = datetime.strptime(value, "%Y-%m-%d")
                queryset = queryset.filter(
                    exam_start_date__gte=query_date,
                    exam_start_date__lt=query_date + timedelta(days=1)
                )
            if field == "examEndDate" and len(value.split("-")) == 3:
                query_date = datetime.strptime(value, "%Y-%m-%d")
                queryset = queryset.filter(
                    exam_end_date__gte=query_date,
                    exam_end_date__lt=query_date + timedelta(days=1)
                )
        return queryset


class CommentViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    """
    Return list of Archived Exams with pagiantion.

    You can filter results by `exam_code`, `event_start` and `event_status`

    Add GET parameter in end of URL, for example:
    `?event_start=1449325446&event_status=Suspicious`
    """
    serializer_class = CommentSerializer
    paginate_by = 25
    queryset = Comment.objects.all()
    authentication_classes = (
        SsoTokenAuthentication, CsrfExemptSessionAuthentication,
        BasicAuthentication)
    permission_classes = (IsAuthenticated, IsProctor)

    def get_queryset(self):
        queryset = Comment.objects.order_by('-pk').all()
        for field, value in self.request.query_params.items():
            if field == "event_status":
                queryset = queryset.filter(event_status=value)
            if field == "event_start":
                queryset = queryset.filter(event_start=value)
            if field == "exam_code":
                queryset = queryset.filter(exam__exam_code=value)
        return queryset

    def create(self, request, *args, **kwargs):
        comment = request.data.get('comment')
        exam = get_object_or_404(
            Exam.objects.by_user_perms(request.user),
            exam_code=request.data.get('examCode')
        )
        Comment.objects.create(
            comment=comment.get('comments'),
            event_status=comment.get('eventStatus'),
            event_start=comment.get('eventStart'),
            event_finish=comment.get('eventFinish'),
            duration=comment.get('duration'),
            exam=exam
        )

        ws_data = {
            'hash': exam.generate_key(),
            'proctor': exam.proctor.username,
            'comments': {
                'comment': comment.get('comments'),
                'timestamp': comment.get('eventStart'),
                'status': comment.get('eventStatus')
            }
        }
        send_ws_msg(ws_data, channel=exam.event.hash_key)

        return Response(status=status.HTTP_201_CREATED)


class PermissionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = PermissionSerializer
    queryset = Permission.objects.all()
    authentication_classes = (
        SsoTokenAuthentication, CsrfExemptSessionAuthentication,
        BasicAuthentication)
    permission_classes = (IsAuthenticated, IsProctorOrInstructor)

    def get_queryset(self):
        return Permission.objects.filter(user=self.request.user).all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        result = {
            Permission.ROLE_PROCTOR: [],
            Permission.ROLE_INSTRUCTOR: []
        }
        if serializer.data:
            result['role'] = serializer.data[0]['role']
        for row in serializer.data:
            result[row['role']].append({
                "object_type": row['object_type'],
                "object_id": row['object_id'],
            })
        return Response(result)
