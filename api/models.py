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
    examStartDate = models.DateTimeField()
    examEndDate = models.DateTimeField()
    noOfStudents = models.IntegerField()
    examId = models.CharField(max_length=64)
    courseId = models.CharField(max_length=64)
    firstName = models.CharField(max_length=60)
    lastName = models.CharField(max_length=60)
    # own fields
    examStatus = models.CharField(max_length=8, choices=EXAM_STATUS_CHOICES,
                                  default=NEW)

    def generate_key(self):
        '''
        generate key for edx
        :return: string
        '''
        return hashlib.md5(
            self.examCode + self.examStartDate + self.examEndDate
        ).hexdigest()
