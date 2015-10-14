import json
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from api.web_soket_methods import send_ws_msg
from models import Exam
from edx_api import start_exam_request, pull_status_request


@api_view(['GET'])
def start_exam(request, attempt_code):
    exam = get_object_or_404(Exam, examCode=attempt_code)

    response = start_exam_request(exam.examCode)
    if response.status_code == 200:
        exam.examStatus = exam.STARTED
        exam.save()
        data = {'status': 'OK'}
    else:
        data = {'error': 'Edx response error. See logs'}
    return Response(data=data, status=response.status_code)


@api_view(['GET'])
def poll_status(request, attempt_code):
    exam = get_object_or_404(Exam, examCode=attempt_code)
    response = pull_status_request(exam.examCode)
    status = json.loads(response.content)
    send_ws_msg(status)
    return Response(data=status, status=response.status_code)
