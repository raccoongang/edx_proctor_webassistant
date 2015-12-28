"""
Views for UI application
"""
# -*- coding: utf-8 -*-
import json
from datetime import datetime, timedelta

from edx_proctor_webassistant.auth import (CsrfExemptSessionAuthentication,
                                           SsoTokenAuthentication,
                                           IsProctor, IsProctorOrInstructor)
from person.models import Permission
from proctoring import models
from proctoring.models import has_permisssion_to_course, Course
from proctoring.serializers import (EventSessionSerializer, CommentSerializer,
                                    ArchivedEventSessionSerializer,
                                    ArchivedExamSerializer)
from django.shortcuts import redirect
from rest_framework import viewsets, status, mixins
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from edx_proctor_webassistant.web_soket_methods import send_ws_msg
from journaling.models import Journaling
from proctoring.edx_api import (start_exam_request, stop_exam_request,
                                poll_status_request, send_review_request,
                                get_proctored_exams_request,
                                bulk_start_exams_request)


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
    """
    Endpoint for exam start
    Exam code sends in the end of URL
    """
    exam = get_object_or_404(
        models.Exam.objects.by_user_perms(request.user),
        exam_code=attempt_code
    )
    response = start_exam_request(exam.exam_code)
    if response.status_code == 200:
        exam.exam_status = exam.STARTED
        exam.proctor = request.user
        exam.attempt_status = "OK"
        exam.save()
        Journaling.objects.create(
            journaling_type=Journaling.EXAM_STATUS_CHANGE,
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
    while attempt < max_retries and current_status != 'submitted':
        response = stop_exam_request(code, action, user_id)
        current_status = _get_status(code)
        attempt += 1
    return response, current_status


# def _stop_exam()

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
    """
    exam = get_object_or_404(
        models.Exam.objects.by_user_perms(request.user),
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
    (SsoTokenAuthentication, CsrfExemptSessionAuthentication)
)
@permission_classes((IsAuthenticated, IsProctor))
def stop_exams(request):
    """
    Endpoint for exam stop
    """
    attempts = request.data.get('attempts')
    if isinstance(attempts, basestring):
        attempts = json.loads(attempts)
    if attempts:
        status_list = []
        for attempt in attempts:
            exam = get_object_or_404(
                models.Exam.objects.by_user_perms(request.user),
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
                models.Exam.objects.by_user_perms(request.user),
                exam_code=val['attempt_code']
            )
            new_status = val['status']
            if (exam.attempt_status == 'ready_to_start'
                and new_status == 'started'):
                exam.actual_start_date = datetime.now()
            if (exam.attempt_status == 'started'
                and new_status == 'submitted') \
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
    Event managwment API

    For **create** send `testing_center`,`course_id`,`course_event_id`
    Other fields filling automatically

    You can **update** only `status` and `notify` fields
    """
    serializer_class = EventSessionSerializer
    queryset = models.InProgressEventSession.objects.all()
    authentication_classes = (SsoTokenAuthentication,
                              CsrfExemptSessionAuthentication,
                              BasicAuthentication)
    permission_classes = (IsAuthenticated, IsProctor)

    def create(self, request, *args, **kwargs):
        """
        Create endpoint for event session
        Validate session and check user permissions before create
        """
        fields_for_create = ['testing_center', 'course_id', 'course_event_id']
        data = {}

        for field in fields_for_create:
            if field == 'course_id':
                if request.data.get('course'):
                    course = Course.objects.get(pk=request.data.get('course'))
                else:
                    course = Course.create_by_course_run(
                        request.data.get(field))
                data['course'] = course.pk
            else:
                data[field] = request.data.get(field)
        # Return existing session if match test_center, course_id and exam_id
        # so the proctor is able to connect to existing session
        data['status'] = models.EventSession.IN_PROGRESS
        sessions = models.InProgressEventSession.objects.filter(
            course_event_id=data.get('course_event_id'),
            course=course.pk,
            testing_center=data.get('testing_center')
        ).order_by('-start_date')
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
            journaling_type=Journaling.EVENT_SESSION_START,
            event=serializer.instance,
            proctor=request.user,
        )
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def partial_update(self, request, *args, **kwargs):
        """
        Endpoint for status, notify and comment updates
        """
        instance = self.get_object()
        fields_for_update = ['status', 'notify', 'comment']
        data = {}

        for field in fields_for_update:
            data[field] = request.data.get(field)
        change_end_date = instance.status == models.EventSession.IN_PROGRESS \
                          and data.get(
            'status') == models.EventSession.ARCHIVED
        if str(instance.status) != data.get('status', ''):
            Journaling.objects.create(
                journaling_type=Journaling.EVENT_SESSION_STATUS_CHANGE,
                event=instance,
                proctor=request.user,
                note="%s -> %s" % (instance.status, data.get('status', ''))
            )
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if change_end_date:
            event_session = models.ArchivedEventSession.objects.get(
                pk=instance.pk)
            event_session.end_date = datetime.now()
            event_session.save()
            serializer = self.get_serializer(event_session)
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
    queryset = models.ArchivedEventSession.objects.order_by('-pk')
    paginate_by = 25
    authentication_classes = (SsoTokenAuthentication,
                              CsrfExemptSessionAuthentication,
                              BasicAuthentication)
    permission_classes = (IsAuthenticated, IsProctorOrInstructor)

    def get_queryset(self):
        queryset = super(ArchivedEventSessionViewSet, self).get_queryset()
        queryset = models.EventSession.update_queryset_with_permissions(
            queryset,
            self.request.user
        )
        params = self.request.query_params
        if "testing_center" in params:
            queryset = queryset.filter(testing_center=params["testing_center"])
        if "proctor" in params:
            try:
                first_name, last_name = params["proctor"].split(" ")
                queryset = queryset.filter(proctor__first_name=first_name,
                                           proctor__last_name=last_name)
            except ValueError:
                queryset = queryset.filter(proctor__username=params["proctor"])
        if "hash_key" in params:
            queryset = queryset.filter(hash_key=params["hash_key"])
        if "course_id" in params:
            queryset = queryset.filter(course_id=params["course_id"])
        if "course_event_id" in params:
            queryset = queryset.filter(
                course_event_id=params["course_event_id"])
        if "start_date" in params:
            try:
                query_date = datetime.strptime(params["start_date"],
                                               "%Y-%m-%d")
                queryset = queryset.filter(
                    start_date__gte=query_date,
                    start_date__lt=query_date + timedelta(days=1)
                )
            except ValueError:
                pass
        if "end_date" in params:
            try:
                query_date = datetime.strptime(params["end_date"], "%Y-%m-%d")
                queryset = queryset.filter(
                    end_date__gte=query_date,
                    end_date__lt=query_date + timedelta(
                        days=1)
                )
            except ValueError:
                pass
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
    authentication_classes = (SsoTokenAuthentication,
                              CsrfExemptSessionAuthentication,
                              BasicAuthentication)
    permission_classes = (IsAuthenticated, IsProctor)

    # EDX can ignore review post save procedure
    # that will result in `Pending` status for student
    # so we need to send review few times
    max_resend_attempts = 3

    def post(self, request):
        """
        Passing review statuses:  `Clean`, `Rules Violation`
        Failing review status: `Not Reviewed`, `Suspicious`
        """
        payload = request.data
        required_fields = ['examMetaData', 'reviewStatus', 'videoReviewLink',
                           'desktopComments']
        for field in required_fields:
            if field not in payload:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        if isinstance(payload['examMetaData'], basestring):
            payload['examMetaData'] = json.loads(payload['examMetaData'])
        if isinstance(payload['desktopComments'], basestring):
            payload['desktopComments'] = json.loads(payload['desktopComments'])
        exam = get_object_or_404(
            models.Exam.objects.by_user_perms(request.user),
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
                models.Comment.objects.get(
                    comment=comment.get('comments'),
                    event_status=comment.get('eventStatus'),
                    exam=exam
                )
            except models.Comment.DoesNotExist:
                models.Comment.objects.get_or_create(
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


@api_view(['GET'])
# @authentication_classes((SsoTokenAuthentication,))
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
@authentication_classes((SsoTokenAuthentication,
                         CsrfExemptSessionAuthentication))
@permission_classes((IsAuthenticated, IsProctor))
def bulk_start_exams(request):
    """
    Start list of exams by exam codes.

    Request example

        {
            "list":['<exam_id_1>','<exam_id_2>']
        }

    """
    exam_codes = request.data.get('list', [])
    exam_list = models.Exam.objects.filter(exam_code__in=exam_codes)
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
        journaling_type=Journaling.BULK_EXAM_STATUS_CHANGE,
        note="%s. %s -> %s" % (
            exam_codes, models.Exam.NEW, models.Exam.STARTED
        ),
        proctor=request.user,
    )
    return Response(status=status.HTTP_200_OK)


def redirect_ui(request):
    """
    Redirect when Angular html5 mode enabled
    """
    return redirect('/#{}'.format(request.path))


class ArchivedExamViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Return list of Archived Exams with pagination.

    You can filter results by `event_hash`, `courseID`, `examStartDate`,
    `examEndDate`, `username`, `email`

    Add GET parameter in end of URL, for example:
    `?examStartDate=2015-12-04&email=test@test.com`
    """
    serializer_class = ArchivedExamSerializer
    paginate_by = 50
    queryset = models.Exam.objects.filter(
        event__status=models.EventSession.ARCHIVED
    ).order_by('-pk')
    authentication_classes = (SsoTokenAuthentication,
                              CsrfExemptSessionAuthentication,
                              BasicAuthentication)
    permission_classes = (IsAuthenticated, IsProctorOrInstructor)

    def get_queryset(self):
        """
        Add filters for queryset
        :return: queryset
        """
        queryset = models.Exam.objects.by_user_perms(self.request.user).filter(
            event__status=models.EventSession.ARCHIVED).order_by('-pk')
        permissions = self.request.user.permission_set
        if permissions.filter(role=Permission.ROLE_PROCTOR).exists():
            is_super_proctor = False
            for permission in permissions.filter(
                role=Permission.ROLE_PROCTOR
            ).all():
                if permission.object_id == "*":
                    is_super_proctor = True
                    break
            if not is_super_proctor:
                queryset = queryset.filter(
                    event__proctor=self.request.user)

        params = self.request.query_params
        if "event_hash" in params:
            queryset = queryset.filter(event__hash_key=params["event_hash"])
        if "courseID" in params:
            queryset = queryset.filter(course__display_name=params["courseID"])
        if "username" in params:
            queryset = queryset.filter(username=params["username"])
        if "email" in params:
            queryset = queryset.filter(email=params["email"])
        if "examStartDate" in params:
            try:
                query_date = datetime.strptime(
                    params["examStartDate"], "%Y-%m-%d"
                )
                queryset = queryset.filter(
                    exam_start_date__gte=query_date,
                    exam_start_date__lt=query_date + timedelta(days=1)
                )
            except ValueError:
                pass
        if "examEndDate" in params:
            try:
                query_date = datetime.strptime(
                    params["examEndDate"], "%Y-%m-%d"
                )
                queryset = queryset.filter(
                    exam_end_date__gte=query_date,
                    exam_end_date__lt=query_date + timedelta(days=1)
                )
            except ValueError:
                pass

        return queryset


class CommentViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    """
    Return list of Archived Exams with pagination.

    You can filter results by `exam_code`, `event_start` and `event_status`

    Add GET parameter in end of URL, for example:
    `?event_start=1449325446&event_status=Suspicious`



    Request example for *adding* new comment for exam :

        {
            "examCode": "<exam_code>",
            "comment": {
                "comment": "comment text",
                "event_status": "Suspicious",
                "event_start": 123,
                "event_finish": 321,
                "duration": 198
            }
        }

    """
    serializer_class = CommentSerializer
    paginate_by = 25
    queryset = models.Comment.objects.order_by('-pk')
    authentication_classes = (SsoTokenAuthentication,
                              CsrfExemptSessionAuthentication,
                              BasicAuthentication)
    permission_classes = (IsAuthenticated, IsProctor)

    def get_queryset(self):
        """
        Add filters for queryset
        :return: queryset
        """
        queryset = super(CommentViewSet, self).get_queryset()
        params = self.request.query_params
        if "event_status" in params:
            queryset = queryset.filter(event_status=params["event_status"])
        if "event_start" in params:
            queryset = queryset.filter(event_start=params["event_start"])
        if "exam_code" in params:
            queryset = queryset.filter(exam__exam_code=params["exam_code"])
        return queryset

    def create(self, request, *args, **kwargs):
        """
        Add new comment. Check is exam exists
        """
        exam = get_object_or_404(
            models.Exam.objects.by_user_perms(request.user),
            exam_code=request.data.get('examCode')
        )
        comment = request.data.get('comment')
        comment['exam'] = exam.pk
        serializer = self.get_serializer(data=comment)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # comment journaling
        Journaling.objects.create(
            journaling_type=Journaling.EXAM_COMMENT,
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
            """ % (
                serializer.data.get('duration'),
                serializer.data.get('event_start'),
                serializer.data.get('event_finish'),
                serializer.data.get('event_status'),
                serializer.data.get('comment'),
            ),
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)
