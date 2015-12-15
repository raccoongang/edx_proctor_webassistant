from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Student(models.Model):
    """
    Student model
    """
    sso_id = models.IntegerField()
    email = models.EmailField()
    first_name = models.CharField(max_length=60, blank=True, null=True)
    last_name = models.CharField(max_length=60, blank=True, null=True)


class Permission(models.Model):
    """
    User permissions model
    """
    TYPE_ORG = 'edxorg'
    TYPE_COURSE = 'edxcourse'
    TYPE_COURSERUN = 'edxcourserun'

    ROLE_PROCTOR = 'proctor'
    ROLE_INSTRUCTOR = 'instructor'

    OBJECT_TYPE_CHOICES = {
        ('*', "*"),
        (TYPE_ORG, _("Organization")),
        (TYPE_COURSE, _("Course")),
        (TYPE_COURSERUN, _("Courserun")),
    }

    ROLES_CHOICES = {
        (ROLE_PROCTOR, _("Proctor")),
        (ROLE_INSTRUCTOR, _("Instructor")),
    }
    user = models.ForeignKey(User)
    object_id = models.CharField(max_length=64)
    object_type = models.CharField(max_length=64,
                                   choices=OBJECT_TYPE_CHOICES)
    role = models.CharField(max_length=10, choices=ROLES_CHOICES,
                            default=ROLE_PROCTOR)

    def _get_exam_field_by_type(self):
        """
        return field name by object type
        :return: str
        """
        fields = {
            self.TYPE_ORG: "course_organization",
            self.TYPE_COURSE: "course_identify",
            self.TYPE_COURSERUN: "course_run"
        }
        return fields[self.object_type]

    def prepare_object_id(self):
        """
        Delete courserun from object_id if object type is course id
        :return: str
        """
        return self.object_id if \
            self.object_type != Permission.TYPE_COURSE else \
            Permission._course_run_to_course(self.object_id)

    @classmethod
    def _course_run_to_course(cls, courserun):
        """
        Delete courserun from string
        :param courserun: str
        :return: str
        """
        try:
            edxorg, edxcourse, edxcourserun = Permission.get_course_data(courserun)
            return "/".join((edxorg, edxcourse))
        except:
            return courserun