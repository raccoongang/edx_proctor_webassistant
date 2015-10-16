import json
import requests
from django.conf import settings


def start_exam_request(attempt_code):
    return requests.get(
        settings.EDX_URL + "api/edx_proctoring/proctoring_launch_callback/start_exam/" + attempt_code
    )


def pull_status_request(attempt_code):
    return requests.get(
        settings.EDX_URL + "api/edx_proctoring/proctoring_poll_status/" + attempt_code
    )


def send_review_request(payload):
    return requests.post(
        settings.EDX_URL + "api/edx_proctoring/proctoring_review_callback/",
        data=json.dumps(payload)
    )
