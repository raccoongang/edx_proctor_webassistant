from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out


class Journaling(models.Model):
    PROCTOR_ENTER = 1
    PROCTOR_EXIT = 2
    EVENT_SESSION_START = 3
    EVENT_SESSION_STATUS_CHANGE = 4
    EXAM_ATTEMPT = 5
    EXAM_STATUS_CHANGE = 6
    EXAM_COMMENT = 7
    BULK_EXAM_STATUS_CHANGE = 8
    EDX_API_CALL = 9
    API_REQUESTS = 10

    TYPE_CHOICES = {
        (PROCTOR_ENTER, _("Proctor's login")),
        (PROCTOR_EXIT, _("Proctor's logout")),
        (EVENT_SESSION_START, _("Start event session")),
        (EVENT_SESSION_STATUS_CHANGE, _("Event session status change")),
        (EXAM_ATTEMPT, _("Exam attempt")),
        (EXAM_STATUS_CHANGE, _("Exam status change")),
        (EXAM_COMMENT, _("Proctor's comment")),
        (BULK_EXAM_STATUS_CHANGE, _("Bulk exam status change")),
        (EDX_API_CALL, _("Call to edX API")),
        (API_REQUESTS, _("API Request from edX")),
    }
    type = models.IntegerField(choices=TYPE_CHOICES, db_index=True)
    event = models.ForeignKey("api.EventSession", blank=True, null=True,
                              db_index=True)
    exam = models.ForeignKey("api.Exam", blank=True, null=True, db_index=True)
    proctor = models.ForeignKey(User, blank=True, null=True, db_index=True)
    note = models.TextField(blank=True, null=True)
    proctor_ip = models.GenericIPAddressField(blank=True, null=True)
    datetime = models.DateTimeField(auto_now=True)


def login_journaling(sender, user, request, **kwargs):
    Journaling.objects.create(
        type=Journaling.PROCTOR_ENTER,
        proctor=user
    )


def logout_journaling(sender, user, request, **kwargs):
    Journaling.objects.create(
        type=Journaling.PROCTOR_EXIT,
        proctor=user
    )


user_logged_in.connect(login_journaling)
user_logged_out.connect(logout_journaling)
