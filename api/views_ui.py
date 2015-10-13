from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from models import Exam
from edx_api import start_exam_request

@api_view(['GET'])
def start_exam(request, attempt_code):
    exam = get_object_or_404(Exam, examCode=attempt_code)
    exam.examStatus = exam.STARTED
    exam.save()

    return start_exam_request(exam.examCode)
