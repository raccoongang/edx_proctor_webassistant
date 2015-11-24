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


def get_proctored_exams():
    return requests.get(
        settings.EDX_URL + "api/extended/courses/proctored",
        headers={'X-Edx-Api-Key': settings.EDX_API_KEY}
    )


def bulk_start_exams_request(exam_list):
    result = []
    for exam in exam_list:
        response = requests.get(
            settings.EDX_URL + "api/edx_proctoring/proctoring_launch_callback/start_exam/" + exam.exam_code
        )
        result.append(exam) if response.status_code == 200 else None
    return result


def bulk_send_review_request(payload_list):
    result = {}
    for payload in payload_list:
        response = requests.post(
            settings.EDX_URL + "api/edx_proctoring/proctoring_review_callback/",
            data=json.dumps(payload, default=date_handler)
        )
        result[payload_list["examMetaData"]["examCode"]] = json.loads(
            response.content)
    return result
