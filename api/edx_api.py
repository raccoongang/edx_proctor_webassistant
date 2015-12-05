# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
from django.conf import settings
from api.utils import date_handler
from journaling.models import Journaling


def start_exam_request(attempt_code):
    return _journaling_request(
        'get',
        "api/edx_proctoring/proctoring_launch_callback/start_exam/" + attempt_code
    )


def stop_exam_request(_id, action, user_id):
    return _journaling_request(
        'put',
        "api/edx_proctoring/v1/proctored_exam/attempt/" + _id,
        json.dumps({'action': action, 'user_id': user_id}),
        {'Content-Type': 'application/json'}
    )


def poll_status_request(codes):
    if isinstance(codes, list):
        res = []
        for code in codes:
            ret = _journaling_request(
                'get',
                "api/edx_proctoring/proctoring_poll_status/" + code
            )
            if ret.status_code == 200:
                payload = ret.json()
                payload['attempt_code'] = code
                res.append(payload)
        return res
    else:
        return []


def send_review_request(payload):
    return _journaling_request(
        'post',
        "api/edx_proctoring/proctoring_review_callback/",
        json.dumps(payload, default=date_handler),
    )


def get_proctored_exams_request():
    return _journaling_request(
        'get',
        "api/extended/courses/proctored",
        headers={'X-Edx-Api-Key': settings.EDX_API_KEY}
    )


def bulk_start_exams_request(exam_list):
    result = []
    for exam in exam_list:
        response = _journaling_request(
            'get',
            "api/edx_proctoring/proctoring_launch_callback/start_exam/" + exam.exam_code,
        )
        result.append(exam) if response.status_code == 200 else None
    return result


def bulk_send_review_request(payload_list):
    result = {}
    for payload in payload_list:
        response = _journaling_request(
            'post',
            "api/edx_proctoring/proctoring_review_callback/",
            json.dumps(payload, default=date_handler)
        )
        result[payload_list["examMetaData"]["examCode"]] = json.loads(
            response.content)
    return result


def _journaling_request(request_type, url, data=None, headers=None):
    if request_type == "post":
        response = requests.post(
            settings.EDX_URL + url,
            data=data,
            headers=headers
        )
    elif request_type == "get":
        response = requests.get(
            settings.EDX_URL + url,
            headers=headers
        )
    elif request_type == "put":
        response = requests.put(
            settings.EDX_URL + url,
            data=data,
            headers=headers
        )
    try:
        result = json.loads(response.content)
    except ValueError:
        soup = BeautifulSoup(response.content)
        h1 = soup.find('h1')
        res_list = []
        if h1:
            res_list.append(h1.get_text())
        pre = soup.find('pre', {"class": "exception_value"})
        if pre:
            res_list.append(pre.get_text())
        if res_list:
            result = "\n ".join(res_list)
        else:
            result = response.content
    try:
        Journaling.objects.create(
            type=Journaling.EDX_API_CALL,
            note="""
            Call url:%s
            Sent data: %s
            Response status: %s
            Response content: %s
            """ % (
                url, unicode(data).encode('utf-8'), str(response.status_code), str(result))
        )
    except:
        pass
    return response
