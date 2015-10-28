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

    examCode = models.CharField(max_length=60, unique=True)
    organization = models.CharField(max_length=60)
    duration = models.IntegerField()
    reviewedExam = models.CharField(max_length=60)
    reviewerNotes = models.CharField(max_length=60)
    examPassword = models.CharField(max_length=60)
    examSponsor = models.CharField(max_length=60)
    examName = models.CharField(max_length=60)
    ssiProduct = models.CharField(max_length=60)
    # org extra
    examStartDate = models.DateTimeField(blank=True, null=True)
    examEndDate = models.DateTimeField(blank=True, null=True)
    noOfStudents = models.IntegerField(blank=True, null=True)
    examId = models.CharField(max_length=64, blank=True, null=True)
    courseId = models.CharField(max_length=64, blank=True, null=True)
    firstName = models.CharField(max_length=60, blank=True, null=True)
    lastName = models.CharField(max_length=60, blank=True, null=True)
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
    examStatus = models.CharField(max_length=8,
                                  choices=EXAM_STATUS_CHOICES,
                                  default=NEW)

    objects = ExamsByUserPermsManager()

    def generate_key(self):
        '''
        generate key for edx
        :return: string
        '''
        return hashlib.md5(
            str(self.examCode) + str(self.firstName) + str(
                self.lastName) + str(self.examId)
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
    firstName = models.CharField(max_length=60, blank=True, null=True)
    lastName = models.CharField(max_length=60, blank=True, null=True)
