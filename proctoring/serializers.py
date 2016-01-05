import re
import json
from dateutil import parser
from collections import OrderedDict
from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from models import (Exam, ArchivedEventSession, Comment,
                    has_permission_to_course, InProgressEventSession, Course)
from person.models import Permission, Student


class JSONSerializerField(serializers.Field):
    """ Serializer for orgExtraField"""
    FIELD_LIST = [
        u'courseID',
        u'email',
        u'examEndDate',
        u'examID',
        u'examStartDate',
        u'firstName',
        u'lastName',
        u'noOfStudents',
        u'userID',
        u'username'
    ]

    def to_internal_value(self, data):
        """
        Validate orgExtra data
        :param data: dict
        :return: dict
        """
        json_data = {}
        if isinstance(data, basestring):
            data = json.loads(data)
        try:
            for field_name in self.FIELD_LIST:
                if field_name in data:
                    json_data[field_name] = data[field_name]
                else:
                    raise serializers.ValidationError(
                        _(
                            "orgExtra fields list incorrect. Missed %s" % field_name))
        except ValueError:
            raise serializers.ValidationError(
                _("orgExtra field value error. Must be json"))
        return json_data

    def to_representation(self, instance):
        """
        Get org extra data from Exam model and make dict.
        """
        result = {}
        for field in self.FIELD_LIST:
            result[field] = getattr(
                instance, JSONSerializerField.get_fieldname(field)
            )
        return result

    @classmethod
    def get_fieldname(csl, field):
        """
        Get fieldname from camelCase format
        :param field: str
        :return: str
        """
        if field == 'courseID':
            result = 'course_identify'
        else:
            result = re.sub('([A-Z]+)', r'_\1', field).lower()
        return result


class ExamSerializer(serializers.ModelSerializer):
    """
    Exam serializer
    """

    class Meta:
        model = Exam
        fields = ('examCode', 'organization', 'duration', 'reviewedExam',
                  'reviewerNotes', 'examPassword', 'examSponsor',
                  'examName', 'ssiProduct', 'orgExtra', 'attempt_status',
                  'hash', 'actual_start_date', 'actual_end_date')

    examCode = serializers.CharField(source='exam_code', max_length=60)
    reviewedExam = serializers.CharField(source='reviewed_exam', max_length=60)
    reviewerNotes = serializers.CharField(source='reviewer_notes',
                                          max_length=60, allow_blank=True)
    examPassword = serializers.CharField(source='exam_password', max_length=60)
    examSponsor = serializers.CharField(source='exam_sponsor', max_length=60)
    examName = serializers.CharField(source='exam_name', max_length=60)
    ssiProduct = serializers.CharField(source='ssi_product', max_length=60)
    actual_start_date = serializers.DateTimeField(read_only=True)
    actual_end_date = serializers.DateTimeField(read_only=True)
    attempt_status = serializers.CharField(read_only=True)
    hash = serializers.SerializerMethodField()

    orgExtra = JSONSerializerField(
        style={'base_template': 'textarea.html'},
    )

    def get_hash(self, obj):
        """
        get hash key for exam
        :param obj: Exam instance
        :return: str
        """
        return obj.generate_key()

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = OrderedDict()
        fields = self._readable_fields

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except AttributeError:
                if isinstance(field, JSONSerializerField):
                    ret[field.field_name] = field.to_representation(instance)
                continue

            if attribute is None:
                ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret

    def validate(self, data):
        """
        Move fields from orgExtra to data and rename fieldname from camelCase
        to underscore
        :param data: data from post/put request
        :return: clean data
        """
        for key, value in data['orgExtra'].items():
            data[JSONSerializerField.get_fieldname(key)] = value
        try:
            course = Course.get_by_course_run(data['course_identify'])
            data['course'] = course
        except ValueError:
            raise serializers.ValidationError("Wrong courseId data")
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course didn't found")
        data['exam_end_date'] = parser.parse(data['exam_end_date'])
        data['exam_start_date'] = parser.parse(data['exam_start_date'])
        student = Student.objects.get_or_create(
            sso_id=data['user_id'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )[0]
        data['student'] = student
        del (data['orgExtra'])
        try:
            Exam(**data).full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return super(ExamSerializer, self).validate(data)


class CommentSerializer(serializers.ModelSerializer):
    """
    Comment serializer
    """
    exam_code = serializers.ReadOnlyField(source='exam.exam_code')
    exam = serializers.PrimaryKeyRelatedField(queryset=Exam.objects.all(),
                                              write_only=True)

    class Meta:
        model = Comment


class ArchivedExamSerializer(ExamSerializer):
    """
    Exam archive serializer
    """
    course_id = serializers.CharField(source='course.display_name')
    comments = CommentSerializer(source='comment_set', many=True)

    class Meta:
        model = Exam
        exclude = (
            'exam_code', 'reviewed_exam', 'reviewer_notes', 'exam_password',
            'exam_sponsor', 'exam_name', 'ssi_product',
            'course_id', 'email', 'exam_end_date', 'exam_id',
            'exam_start_date', 'actual_start_date', 'actual_end_date',
            'first_name', 'last_name', 'no_of_students', 'user_id', 'username')


class EventSessionSerializer(serializers.ModelSerializer):
    """
    Event session serializer
    """
    hash_key = serializers.CharField(read_only=True)
    start_date = serializers.DateTimeField(read_only=True)
    end_date = serializers.DateTimeField(read_only=True)
    course_id = serializers.SerializerMethodField()
    course_name = serializers.SerializerMethodField()
    owner_username = serializers.SerializerMethodField()

    def get_owner_username(self, obj):
        return obj.proctor.username

    def get_course_name(self, obj):
        return obj.course.course_name

    def get_course_id(self, obj):
        return obj.course.display_name

    class Meta:
        model = InProgressEventSession

    def validate(self, data):
        """
        Data validation
        :param data: data from post/put request
        :return: clean data
        """
        if not self.partial:
            if not self.instance and not has_permission_to_course(
                data.get('proctor'),
                data.get('course').get_full_course()
            ):
                raise serializers.ValidationError(
                    "You have not permissions to create event for this course")
        return super(EventSessionSerializer, self).validate(data)


class ArchivedEventSessionSerializer(serializers.ModelSerializer):
    """
    Event session archive serializer
    """
    course_id = serializers.SerializerMethodField()
    proctor = serializers.SerializerMethodField()
    serializers.ReadOnlyField(source='proctor.username')

    def get_course_id(self, obj):
        return obj.course.display_name

    def get_proctor(self, obj):
        proctor = obj.proctor
        return ' '.join([proctor.first_name,
                         proctor.last_name]).strip() or proctor.username

    class Meta:
        read_only_fields = (
            'testing_center', 'course_id', 'course_event_id', 'proctor',
            'status', 'hash_key', 'notify', 'start_date', 'end_date', 'comment'
        )
        model = ArchivedEventSession
