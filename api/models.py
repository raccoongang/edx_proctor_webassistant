import hashlib
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User


class ExamsByUserPermsManager(models.Manager):
    def by_user_perms(self, user):
        qs = super(ExamsByUserPermsManager, self).get_queryset()
        return qs


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
    courseOrganization = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        db_index=True
    )
    courseIdentify = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        db_index=True
    )
    courseRun = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        db_index=True
    )
    examStatus = models.CharField(max_length=8, choices=EXAM_STATUS_CHOICES,
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
    user = models.ForeignKey(User)
    object_id = models.CharField(max_length=64)
    object_type = models.CharField(max_length=64)  # org, course, course_run


class Student(models.Model):
    sso_id = models.IntegerField()
    email = models.EmailField()
    firstName = models.CharField(max_length=60, blank=True, null=True)
    lastName = models.CharField(max_length=60, blank=True, null=True)
