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
    r = requests.post(
        settings.EDX_URL + "api/extended/courses/proctored"
    )
    r.headers.update({'X-Edx-Api-Key': settings.EDX_API_KEY})
    return r


def bulk_start_exams_request(exam_list):
    exams = [exam.exam_code for exam in exam_list]
    response = requests.get(
        settings.EDX_URL + "/api/edx_proctoring/proctoring_launch_callback/bulk_start_exams/" + ",".join(exams)
    )
    return json.loads(response.content)


def bulk_send_review_request(payload_list):
    response = requests.post(
            settings.EDX_URL + "api/edx_proctoring/proctoring_bulk_review_callback/",
            data=json.dumps(payload_list, default=date_handler)
        )
    return json.loads(response.content)
