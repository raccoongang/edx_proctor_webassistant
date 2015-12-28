from rest_framework import serializers

from journaling.models import Journaling


class JournalingSerializer(serializers.ModelSerializer):
    """
    Journaling serializer
    """
    proctor = serializers.ReadOnlyField(source='proctor.username')
    event = serializers.ReadOnlyField(source='event.hash_key')
    exam_code = serializers.ReadOnlyField(source='exam.exam_code')
    type_name = serializers.SerializerMethodField()
    student = serializers.SerializerMethodField()

    def get_student(self, obj):
        """
        Get student data
        :param obj: Journaling instance
        :return: str
        """
        return obj.get_student()

    def get_type_name(self, obj):
        """
        Get userfriendly type name
        :param obj:
        :return:
        """
        return obj.get_journaling_type_display()

    class Meta:
        model = Journaling
        exclude = ("exam",)


