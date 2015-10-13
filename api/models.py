import hashlib
from django.db import models
from django.utils.translation import ugettext_lazy as _


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

    examCode = models.CharField(max_length=60)
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
    examStatus = models.CharField(max_length=8, choices=EXAM_STATUS_CHOICES,
                                  default=NEW)

    def generate_key(self):
        '''
        generate key for edx
        :return: string
        '''
        return hashlib.md5(
            str(self.examCode) + str(self.examStartDate) + str(
                self.examEndDate)
        ).hexdigest()
