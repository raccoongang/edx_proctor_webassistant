from rest_framework import serializers
import json
from django.utils.translation import ugettext as _


class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""

    def to_internal_value(self, data):
        field_list = {
            'examStartDate',
            'examEndDate',
            'noOfStudents',
            'examID',
            'courseID',
            'firstName',
            'lastName',
        }
        json_data = {}
        try:
            json_data = json.loads(data)
            if cmp(json_data.keys(), field_list) != 0:
                raise serializers.ValidationError(
                    _("orgExtra fields list incorrect"))

        except ValueError, e:
            raise serializers.ValidationError(
                _("orgExtra field value error. Must be json"))
        finally:
            return json_data

    def to_representation(self, value):
        return value


class RegisterExamAttemptSerializer(serializers.Serializer):
    examCode = serializers.CharField(max_length=60)
    organization = serializers.CharField(max_length=60)
    duration = serializers.IntegerField()
    reviewedExam = serializers.CharField(max_length=60)
    reviewerNotes = serializers.CharField(max_length=60)
    examPassword = serializers.CharField(max_length=60)
    examSponsor = serializers.CharField(max_length=60)
    examName = serializers.CharField(max_length=60)
    ssiProduct = serializers.CharField(max_length=60)
    orgExtra = serializers.CharField(
        max_length=60,
        style={'base_template': 'textarea.html'},
    )
