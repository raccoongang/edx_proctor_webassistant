# -*- coding: utf-8 -*-
import hashlib
import operator
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, AnonymousUser
from django.db.models import Q

from person.models import Student, Permission


class Course(models.Model):
    """
    Course model
    """
    course_org = models.CharField(max_length=60)
    course_id = models.CharField(max_length=60)
    course_run = models.CharField(max_length=60)
    display_name = models.CharField(max_length=60)
    course_name = models.CharField(max_length=128, blank=True, null=True)

    def get_full_course(self):
        """
        Slash separated org, id and course run
        :return: str
        """
        return "/".join((self.course_org, self.course_id, self.course_run))

    @classmethod
    def get_by_course_run(cls, course_run):
        """
        Get Course by course string
        :param course_run: str
        :return: Course object
        """
        course_org, course_id, course_run = Course.get_course_data(course_run)
        return Course.objects.get(
            course_org=course_org,
            course_id=course_id,
            course_run=course_run
        )

    @classmethod
    def create_by_course_run(cls, name):
        """
        Create Course by course string
        :param name: str
        :return: Course object
        """
        course_org, course_id, course_run = Course.get_course_data(name)
        return cls.objects.get_or_create(
            course_org=course_org,
            course_id=course_id,
            course_run=course_run,
            display_name=name
        )[0]

    @classmethod
    def get_course_data(cls, course_id):
        """
        Check course format and return list using separator
        :param course_id: str
        :return: list
        """
        sp = course_id.split(':')
        if len(sp) == 2:
            return sp[-1].split('+')
        else:
            return course_id.split('/')

    @classmethod
    def filter_courses_by_permission(cls, q_objects, permission):
        """
        Queryset by permission
        :param q_objects: queryset
        :param permission: Permission object
        :return: queryset
        """
        if permission.object_type == Permission.TYPE_ORG:
            q_objects.append(Q(**{
                "course__course_org":
                    permission.prepare_object_id()
            }))
        elif permission.object_type == Permission.TYPE_COURSE:
            course_org, course_id, course_run = Course.get_course_data(
                permission.object_id)
            q_objects.append(Q(**{
                "course__course_org": course_org,
                "course__course_id": course_id,
            }))
        else:
            course_org, course_id, course_run = Course.get_course_data(
                permission.object_id)
            q_objects.append(Q(**{
                "course__course_org": course_org,
                "course__course_id": course_id,
                "course__course_run": course_run,
            }))

        return q_objects

    def __unicode__(self):
        return self.display_name


def has_permission_to_course(user, course_id, permissions=None, role=None):
    """
    Check is user has access to this course
    :param user: User instance
    :param course_id: str
    :param permissions: list of all user's permissions
    :param role: role of user
    :return: bool
    """
    course_data = {}
    try:
        edxorg, edxcourse, edxcourserun = Course.get_course_data(course_id)
        course_data['edxorg'] = edxorg
        course_data['edxcourse'] = "/".join((edxorg, edxcourse))
        course_data['edxcourserun'] = "/".join(
            (edxorg, edxcourse, edxcourserun))
    except ValueError as e:
        return False
    if not isinstance(user, AnonymousUser):
        if user.is_superuser:
            return True
        permissions = permissions if permissions else user.permission_set.all()
        if role:
            permissions = permissions.filter(role=role)
        for permission in permissions:
            if permission.object_id != "*":
                if course_data.get(
                    permission.object_type
                ) == permission.prepare_object_id():
                    return True
            else:
                return True
    return False


class ExamsByUserPermsManager(models.Manager):
    """
    Manager for getting list of exams consider permissions
    """

    def by_user_perms(self, user):
        """
        Update queryset consider permissions
        :param user: User instance
        :return: queryset
        """
        qs = super(ExamsByUserPermsManager, self).get_queryset()
        q_objects = []
        if not isinstance(user, AnonymousUser):
            if user.is_superuser:
                return qs
            for permission in user.permission_set.all():
                if permission.object_id != "*":
                    q_objects = Course.filter_courses_by_permission(
                        q_objects, permission
                    )
                else:
                    return qs
            if len(q_objects):
                return qs.filter(reduce(operator.or_, q_objects))

        return qs.filter(pk__lt=0)


class Exam(models.Model):
    """
    Exam model
    """
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
    reviewer_notes = models.CharField(max_length=60, blank=True, null=True)
    exam_password = models.CharField(max_length=60)
    exam_sponsor = models.CharField(max_length=60)
    exam_name = models.CharField(max_length=60)
    ssi_product = models.CharField(max_length=60)
    # org extra
    exam_start_date = models.DateTimeField(blank=True, null=True)
    exam_end_date = models.DateTimeField(blank=True, null=True)
    actual_start_date = models.DateTimeField(blank=True, null=True)
    actual_end_date = models.DateTimeField(blank=True, null=True)
    no_of_students = models.IntegerField(blank=True, null=True)
    exam_id = models.CharField(max_length=64, blank=True, null=True)
    course_identify = models.CharField(max_length=64, blank=True, null=True)
    first_name = models.CharField(max_length=60, blank=True, null=True)
    last_name = models.CharField(max_length=60, blank=True, null=True)
    email = models.EmailField(max_length=60, blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    username = models.CharField(max_length=50, blank=True, null=True)
    # own fields
    course = models.ForeignKey(Course)
    student = models.ForeignKey(Student)
    proctor = models.ForeignKey(User, blank=True, null=True)
    exam_status = models.CharField(
        max_length=8,
        choices=EXAM_STATUS_CHOICES,
        default=NEW)

    attempt_status = models.CharField(max_length=20, blank=True, null=True)

    event = models.ForeignKey('EventSession', blank=True, null=True)

    objects = ExamsByUserPermsManager()

    def generate_key(self):
        """
        generate key for edx
        :return: string
        """
        str_to_hash = str(self.exam_code) + str(self.user_id) + str(
            self.exam_id) + str(self.email)
        return hashlib.md5(str_to_hash).hexdigest()

    def __unicode__(self):
        return self.exam_id


class InProgressEventSessionManager(models.Manager):
    """
    Manager for getting all active Event Sessions
    """

    def get_queryset(self):
        return super(InProgressEventSessionManager,
                     self).get_queryset().exclude(
            status=EventSession.ARCHIVED)


class ArchivedEventSessionManager(models.Manager):
    """
    Manager for getting all finished Event Sessions
    """

    def get_queryset(self):
        return super(ArchivedEventSessionManager, self).get_queryset().filter(
            status=EventSession.ARCHIVED)


class EventSession(models.Model):
    """
    Event session model
    Attention! hash key generates only for InProgressEventSession proxy model
    """
    IN_PROGRESS = 'in_progress'
    ARCHIVED = 'archived'

    SESSION_STATUS_CHOICES = {
        (IN_PROGRESS, _("In progress")),
        (ARCHIVED, _("Archived")),
    }
    testing_center = models.CharField(max_length=128)
    course = models.ForeignKey(Course)
    course_event_id = models.CharField(max_length=128, blank=True, null=True)
    proctor = models.ForeignKey(User)
    status = models.CharField(
        max_length=11,
        choices=SESSION_STATUS_CHOICES,
        default=IN_PROGRESS
    )
    hash_key = models.CharField(max_length=128, db_index=True, blank=True,
                                null=True)
    notify = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    exam_name = models.CharField(max_length=128, blank=True, null=True)

    @staticmethod
    def update_queryset_with_permissions(queryset, user):
        """
        Update queryset consider permissions
        :param queryset: queryset
        :param user: User instance
        :return: queryset
        """
        if user.permission_set.filter(
            role=Permission.ROLE_PROCTOR).exists():
            is_super_proctor = False
            for permission in user.permission_set.filter(
                role=Permission.ROLE_PROCTOR).all():
                if permission.object_id == "*":
                    is_super_proctor = True
                    break
            if not is_super_proctor:
                queryset = queryset.filter(
                    proctor=user)
        elif user.permission_set.filter(role=Permission.ROLE_INSTRUCTOR
                                        ).exists():
            for permission in user.permission_set.filter(
                role=Permission.ROLE_INSTRUCTOR).all():
                q_objects = []
                if permission.object_id != "*":
                    q_objects = Course.filter_courses_by_permission(
                        q_objects, permission
                    )
            if len(q_objects):
                queryset = queryset.filter(reduce(operator.or_, q_objects))

        return queryset

    @staticmethod
    def post_save(sender, instance, created, **kwargs):
        """
        Method for post save signal.
        Add hash key, add slashseparated course_run
        :param sender:
        :param instance:
        :param created:
        :param kwargs:
        :return:
        """
        if created and not instance.hash_key:
            instance.hash_key = hashlib.md5(
                unicode(instance.testing_center).encode('utf-8') + str(
                    instance.course.course_run) + str(
                    instance.course_event_id) + str(instance.proctor.pk) + str(
                    instance.start_date)).hexdigest()
            instance.save()

    def __unicode__(self):
        return u" | ".join((self.testing_center,
                            self.course.course_run,
                            self.course_event_id))


class InProgressEventSession(EventSession):
    """
    Proxy model for active event sessions
    """

    class Meta:
        proxy = True

    objects = InProgressEventSessionManager()


class ArchivedEventSession(EventSession):
    """
    Proxy model for finished event sessions
    """

    class Meta:
        proxy = True

    objects = ArchivedEventSessionManager()


post_save.connect(InProgressEventSession.post_save, InProgressEventSession,
                  dispatch_uid='add_hash')


class Comment(models.Model):
    """
    Comment model
    """
    comment = models.TextField()
    event_status = models.CharField(max_length=60)
    event_start = models.IntegerField()
    event_finish = models.IntegerField()
    exam = models.ForeignKey(Exam)
    duration = models.IntegerField(blank=True, null=True)
