import hashlib
import operator

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, AnonymousUser
from django.db.models import Q


class ExamsByUserPermsManager(models.Manager):
    def by_user_perms(self, user):
        qs = super(ExamsByUserPermsManager, self).get_queryset()
        q_objects = []
        if not isinstance(user, AnonymousUser):
            for permission in user.permission_set.all():
                if permission.object_id != "*":
                    q_objects.append(Q(**{permission._get_exam_field_by_type():
                                              permission.object_id}))
                else:
                    return qs
            if len(q_objects):
                return qs.filter(reduce(operator.or_, q_objects))

        return []


class Exam(models.Model):
    NEW = 'new'
    STARTED = 'started'
    FINISHED = 'finished'
    FAILED = 'failed'

    EXAM_STATUS_CHOICES = {
        (NEW, _("Not started")),
        (STARTED, _("Started")),
        (FINISHED, _("Finished")),
        (FAILED, _("Failed")),
    }

    exam_code = models.CharField(max_length=60, unique=True)
    organization = models.CharField(max_length=60)
    duration = models.IntegerField()
    reviewed_exam = models.CharField(max_length=60)
    reviewer_notes = models.CharField(max_length=60)
    exam_password = models.CharField(max_length=60)
    exam_sponsor = models.CharField(max_length=60)
    exam_name = models.CharField(max_length=60)
    ssi_product = models.CharField(max_length=60)
    # org extra
    exam_start_date = models.DateTimeField(blank=True, null=True)
    exam_end_date = models.DateTimeField(blank=True, null=True)
    no_of_students = models.IntegerField(blank=True, null=True)
    exam_id = models.CharField(max_length=64, blank=True, null=True)
    course_id = models.CharField(max_length=64, blank=True, null=True)
    first_name = models.CharField(max_length=60, blank=True, null=True)
    last_name = models.CharField(max_length=60, blank=True, null=True)
    # own fields
    course_organization = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        db_index=True
    )
    course_identify = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        db_index=True
    )
    course_run = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        db_index=True
    )
    exam_status = models.CharField(
        max_length=8,
        choices=EXAM_STATUS_CHOICES,
        default=NEW)

    objects = ExamsByUserPermsManager()

    def generate_key(self):
        '''
        generate key for edx
        :return: string
        '''
        return hashlib.md5(
            str(self.exam_code) + str(self.first_name) + str(
                self.last_name) + str(self.exam_id)
        ).hexdigest()


class Permission(models.Model):
    TYPE_ORG = 'edxorg'
    TYPE_COURSE = 'edxcourse'
    TYPE_COURSERUN = 'edxcourserun'

    OBJECT_TYPE_CHOICES = {
        (TYPE_ORG, _("Organization")),
        (TYPE_COURSE, _("Course")),
        (TYPE_COURSERUN, _("Courserun")),
    }
    user = models.ForeignKey(User)
    object_id = models.CharField(max_length=64)
    object_type = models.CharField(max_length=64,
                                   choices=OBJECT_TYPE_CHOICES)

    def _get_exam_field_by_type(self):
        fields = {
            self.TYPE_ORG: "course_organization",
            self.TYPE_COURSE: "course_identify",
            self.TYPE_COURSERUN: "course_run"
        }
        return fields[self.object_type]


class Student(models.Model):
    sso_id = models.IntegerField()
    email = models.EmailField()
    first_name = models.CharField(max_length=60, blank=True, null=True)
    last_name = models.CharField(max_length=60, blank=True, null=True)
