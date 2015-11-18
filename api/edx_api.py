import json
import requests
from django.conf import settings
from api.utils import date_handler


def start_exam_request(attempt_code):
    return requests.get(
        settings.EDX_URL + "api/edx_proctoring/proctoring_launch_callback/start_exam/" + attempt_code
    )


def poll_status_request(attempt_code):
    return requests.get(
        settings.EDX_URL + "api/edx_proctoring/proctoring_poll_status/" + attempt_code
    )


def send_review_request(payload):
    return requests.post(
        settings.EDX_URL + "api/edx_proctoring/proctoring_review_callback/",
        data=json.dumps(payload, default=date_handler)
    )


def get_proctored_exams(payload):
    return requests.post(
        settings.EDX_URL + "api/edx_proctoring/proctoring_review_callback/",
        data=json.dumps(payload, default=date_handler)
    )

def bulk_start_exams_request(exam_list):
    for exam in exam_list:
        result = {}
        response = requests.get(
            settings.EDX_URL + "api/edx_proctoring/proctoring_launch_callback/start_exam/" + attempt_code
        )
        result[exam.exam_code] = json.loads(response.content)
    return result
