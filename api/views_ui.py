import json
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from api.web_soket_methods import send_ws_msg
from models import Exam
from edx_api import start_exam_request, poll_status_request, \
    send_review_request


@api_view(['GET'])
def start_exam(request, attempt_code):
    exam = get_object_or_404(Exam, examCode=attempt_code)

    response = start_exam_request(exam.examCode)
    if response.status_code == 200:
        exam.examStatus = exam.STARTED
        exam.save()
        data = {
            'hash': exam.generate_key(),
            'status': "OK"
        }
        send_ws_msg(data)
    else:
        data = {'error': 'Edx response error. See logs'}
    return Response(data=data, status=response.status_code)


@api_view(['GET'])
def poll_status(request, attempt_code):
    exam = get_object_or_404(Exam, examCode=attempt_code)
    response = poll_status_request(exam.examCode)
    status = json.loads(response.content)
    data = {
        'hash': exam.generate_key(),
        'status': status.get('status')
    }
    send_ws_msg(data)
    return Response(data=data, status=response.status_code)


@api_view(['POST'])
def review(request):
    """
    Request example:

    `{"attempt_code":"029288A9-9198-4C99-9D3F-E589695CF5D7"}`

    """
    passing_review_status = ['Clean', 'Rules Violation']
    failing_review_status = ['Not Reviewed', 'Suspicious']
    exam = get_object_or_404(Exam, examCode=request.data.get('attempt_code'))

    review_payload = {
        "examDate": "",
        "examProcessingStatus": "Review Completed",
        "examTakerEmail": "",
        "examTakerFirstName": "John",
        "examTakerLastName": "Doe",
        "keySetVersion": "",
        "examApiData": {
            "duration": exam.duration,
            "examCode": exam.examCode,
            "examName": exam.examName,
            "examPassword": exam.examPassword,
            "examSponsor": exam.examSponsor,
            "examUrl": "http://localhost:8000/api/edx_proctoring/proctoring_launch_callback/start_exam/4d07a01a-1502-422e-b943-93ac04dc6ced",
            "orgExtra": {
                "courseID": exam.courseId,
                "examEndDate": exam.examEndDate,
                "examID": exam.examId,
                "examStartDate": exam.examStartDate,
                "noOfStudents": exam.noOfStudents
            },
            "organization": exam.organization,
            "reviewedExam": exam.reviewedExam,
            "reviewerNotes": exam.reviewerNotes,
            "ssiProduct": "rp-now"
        },
        "overAllComments": "",
        "reviewStatus": passing_review_status[0],
        "userPhotoBase64String": "",
        "videoReviewLink": "",
        "examMetaData": {
            "examCode": request.data.get('attempt_code'),
            "examName": exam.examName,
            "examSponsor": exam.examSponsor,
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
    if response.status_code == 200:
        data = {'status': 'review has sent'}
    else:
        data = {'error': "send review failed"}

    return Response(data=data,
                    status=response.status_code)
