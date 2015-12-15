from rest_framework import serializers

from person.models import Permission


class PermissionSerializer(serializers.ModelSerializer):
    object_id = serializers.SerializerMethodField()

    def get_object_id(self, obj):
        """
        Delete course run
        :param obj:
        :return:
        """
        return obj.prepare_object_id()

    class Meta:
        model = Permission
        exclude = ("id", "user")
