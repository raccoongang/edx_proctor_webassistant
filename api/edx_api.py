import requests
from django.conf import settings


def start_exam_request(attempt_code):
    return requests.get(
        settings.EDX_URL + "edx_proctoring/proctoring_launch_callback/start_exam/" + attempt_code)
