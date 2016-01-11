"""
Views for UI application
"""
from datetime import datetime, timedelta

from rest_framework import mixins, viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from edx_proctor_webassistant.auth import SsoTokenAuthentication, \
    CsrfExemptSessionAuthentication, IsProctor
from journaling.models import Journaling
from journaling.serializers import JournalingSerializer


class JournalingViewSet(mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """
    Return list of Journaling with pagiantion.

    You can filter results by `event_hash`, `proctor`,`exam_code`,
    `type`, `date`

    Add GET parameter in end of URL, for example:

    `?date=2015-12-04&type=8`

    """
    serializer_class = JournalingSerializer
    queryset = Journaling.objects.order_by('-pk')
    paginate_by = 25
    authentication_classes = (
        SsoTokenAuthentication, CsrfExemptSessionAuthentication,
        BasicAuthentication)
    permission_classes = (IsAuthenticated, IsProctor)

    def get_queryset(self):
        """
        Add filters for queryset
        :return: queryset
        """

        queryset = super(JournalingViewSet, self).get_queryset()
        params = self.request.query_params
        if "proctor" in params:
            queryset = queryset.filter(proctor__username=params["proctor"])
        if "exam_code" in params:
            queryset = queryset.filter(exam__exam_code=params["exam_code"])
        if "type" in params:
            queryset = queryset.filter(journaling_type=params["type"])
        if "event_hash" in params:
            queryset = queryset.filter(event__hash_key=params["event_hash"])
        if "date" in params:
            try:
                query_date = datetime.strptime(params["date"], "%Y-%m-%d")
                queryset = queryset.filter(
                    datetime__gte=query_date,
                    datetime__lt=query_date + timedelta(days=1)
                )
            except ValueError:
                pass

        return queryset
