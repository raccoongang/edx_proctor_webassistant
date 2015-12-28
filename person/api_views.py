from rest_framework import mixins, viewsets, status
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from edx_proctor_webassistant.auth import SsoTokenAuthentication, \
    CsrfExemptSessionAuthentication, IsProctorOrInstructor
from person.models import Permission
from person.serializers import PermissionSerializer


class PermissionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Endpoint wich shows all permissions for current user
    """
    serializer_class = PermissionSerializer
    queryset = Permission.objects.all()
    authentication_classes = (SsoTokenAuthentication,
                              CsrfExemptSessionAuthentication,
                              BasicAuthentication)
    permission_classes = (IsAuthenticated, IsProctorOrInstructor)

    def get_queryset(self):
        """
        Return permissions only for current user
        :return: queryset
        """
        queryset = super(PermissionViewSet, self).get_queryset()
        return queryset.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """
        Separate permissions by role
        :param request:
        :param args:
        :param kwargs:
        :return: response
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        result = {
            Permission.ROLE_PROCTOR: [],
            Permission.ROLE_INSTRUCTOR: []
        }
        if serializer.data:
            result['role'] = serializer.data[0]['role']
        for row in serializer.data:
            result[row['role']].append({
                "object_type": row['object_type'],
                "object_id": row['object_id'],
            })
        return Response(result, status=status.HTTP_200_OK)
