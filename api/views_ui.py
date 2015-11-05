import json
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import BasicAuthentication
from api.web_soket_methods import send_ws_msg
from models import Exam
from edx_api import start_exam_request, poll_status_request, \
    send_review_request
from api.auth import CsrfExemptSessionAuthentication


@api_view(['GET'])
def start_exam(request, attempt_code):
    exam = get_object_or_404(Exam, exam_code=attempt_code)

    response = start_exam_request(exam.exam_code)
    if response.status_code == 200:
        exam.exam_status = exam.STARTED
        exam.proctor = request.user
        exam.save()
        data = {
            'hash': exam.generate_key(),
            'proctor': exam.proctor.username,
            'status': "OK"
        }
        send_ws_msg(data)
    else:
        data = {'error': 'Edx response error. See logs'}
    return Response(data=data, status=response.status_code)


@api_view(['GET'])
def poll_status(request, attempt_code):
    exam = get_object_or_404(Exam, exam_code=attempt_code)
    response = poll_status_request(exam.exam_code)
    status = json.loads(response.content)
    data = {
        'hash': exam.generate_key(),
        'status': status.get('status')
    }
    send_ws_msg(data)
    return Response(data=data, status=response.status_code)


class Review(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request):
        """
        Request example:

        `{"attempt_code":"029288A9-9198-4C99-9D3F-E589695CF5D7"}`

        """
        passing_review_status = ['Clean', 'Rules Violation']
        failing_review_status = ['Not Reviewed', 'Suspicious']
        exam = get_object_or_404(Exam, exam_code=request.data.get('attempt_code'))

        review_payload = {
            "examDate": "",
            "examProcessingStatus": "Review Completed",
            "examTakerEmail": "",
            "examTakerFirstName": "John",
            "examTakerLastName": "Doe",
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
            "reviewStatus": passing_review_status[0],
            "userPhotoBase64String": "",
            "videoReviewLink": "",
            "examMetaData": {
                "examCode": request.data.get('attempt_code'),
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
            "desktopComments": [
                {
                    "comments": "Browsing other websites",
                    "duration": 88,
                    "eventFinish": 88,
                    "eventStart": 12,
                    "eventStatus": "Suspicious"
                },
            ],
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

        response = send_review_request(review_payload)
        data = {
            'hash': exam.generate_key(),
            'status': ''
        }
        if response.status_code == 200:
            data['status'] = 'review_was_sent'
        else:
            data['status'] = 'send review failed'

        return Response(data=data,
                        status=response.status_code)
