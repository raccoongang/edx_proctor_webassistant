import re
import json
from dateutil import parser
from collections import OrderedDict
from rest_framework import serializers
from rest_framework.fields import SkipField

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from models import Exam, EventSession


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
        Field value -> String.
        """
        result = {}
        for field in self.FIELD_LIST:
            result[field] = getattr(
                instance, re.sub('([A-Z]+)', r'_\1', field).lower()
            )
        return result


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ('examCode', 'organization', 'duration', 'reviewedExam',
                  'reviewerNotes', 'examPassword', 'examSponsor',
                  'examName', 'ssiProduct', 'orgExtra')

    examCode = serializers.CharField(source='exam_code', max_length=60)
    reviewedExam = serializers.CharField(source='reviewed_exam', max_length=60)
    reviewerNotes = serializers.CharField(source='reviewer_notes',
                                          max_length=60, allow_blank=True)
    examPassword = serializers.CharField(source='exam_password', max_length=60)
    examSponsor = serializers.CharField(source='exam_sponsor', max_length=60)
    examName = serializers.CharField(source='exam_name', max_length=60)
    ssiProduct = serializers.CharField(source='ssi_product', max_length=60)

    orgExtra = JSONSerializerField(
        style={'base_template': 'textarea.html'},
    )

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = OrderedDict()
        fields = self._readable_fields

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue
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
        '''
        Data validation
        :param data: data from post/put request
        :return: clean data
        '''
        # move fields from orgExtra to data and rename fieldname from camelCase
        # to underscore
        for key, value in data['orgExtra'].items():
            data[re.sub('([A-Z]+)', r'_\1', key).lower()] = value
        try:
            course_org, course_id, course_run = Exam.get_course_data(
                data['course_id'])
        except ValueError as e:
            raise serializers.ValidationError("Wrong courseId data")
        data['course_organization'] = course_org
        data['course_identify'] = "/".join((course_org, course_id))
        data['course_run'] = data['course_id']
        data['exam_end_date'] = parser.parse(data['exam_end_date'])
        data['exam_start_date'] = parser.parse(data['exam_start_date'])
        del (data['orgExtra'])
        try:
            Exam(**data).full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return super(ExamSerializer, self).validate(data)


class EventSessionSerializer(serializers.ModelSerializer):
    hash_key = serializers.CharField(read_only=True)
    start_date = serializers.DateTimeField(read_only=True)
    end_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = EventSession
