from collections import OrderedDict
from django.core.exceptions import ValidationError
from rest_framework import serializers
import json
from django.utils.translation import ugettext as _
from rest_framework.fields import SkipField

from models import Exam


class JSONSerializerField(serializers.Field):
    """ Serializer for orgExtraField"""
    FIELD_LIST = [
        'examStartDate',
        'examEndDate',
        'noOfStudents',
        'examId',
        'courseId',
        'firstName',
        'lastName',
    ]

    def to_internal_value(self, data):
        json_data = {}
        try:
            json_data = json.loads(data)
            if cmp(json_data.keys(), self.FIELD_LIST) != 0:
                raise serializers.ValidationError(
                    _("orgExtra fields list incorrect"))
        except ValueError:
            raise serializers.ValidationError(
                _("orgExtra field value error. Must be json"))
        finally:
            return json_data

    def to_representation(self, instance):
        """
        Field value -> String.
        """
        result = {}
        for field in self.FIELD_LIST:
            result[field] = getattr(instance, field)
        return result


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ('examCode', 'organization', 'duration', 'reviewedExam',
                  'reviewerNotes', 'examPassword', 'examSponsor',
                  'examName', 'ssiProduct', 'orgExtra')

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
        data.update(data['orgExtra'])
        try:
            course_org, course_id, course_run = data['courseId'].split('/')
            data['course_organization'] = course_org
            data['course_identify'] = "/".join((course_org, course_id))
            data['course_run'] = data['courseId']
        except ValueError as e:
            raise serializers.ValidationError("Wrong courseId data")

        del (data['orgExtra'])
        try:
            Exam(**data).full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return super(ExamSerializer, self).validate(data)
