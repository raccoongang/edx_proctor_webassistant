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
    queryset = Journaling.objects.order_by('-pk').all()
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
        queryset = Journaling.objects.order_by('-pk').all()
        for field, value in self.request.query_params.items():
            if field == "proctor":
                queryset = queryset.filter(proctor__username=value)
            if field == "exam_code":
                queryset = queryset.filter(exam__exam_code=value)
            if field == "type":
                queryset = queryset.filter(type=value)
            if field == "event_hash":
                queryset = queryset.filter(event__hash_key=value)
            if field == "date" and len(value.split("-")) == 3:
                query_date = datetime.strptime(value, "%Y-%m-%d")
                queryset = queryset.filter(
                    datetime__gte=query_date,
                    datetime__lt=query_date + timedelta(days=1)
                )
        return queryset