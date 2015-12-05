import json
from rest_framework.authentication import SessionAuthentication, \
    TokenAuthentication
from social.apps.django_app.default.models import UserSocialAuth
from rest_framework import exceptions
from rest_framework.permissions import BasePermission
from django.utils.translation import ugettext_lazy as _


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class SsoTokenAuthentication(TokenAuthentication):
    model = UserSocialAuth

    def authenticate_credentials(self, key):
        try:
            token = self.model.objects.select_related('user').get(extra_data={"access_token": key})
        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))


        return (token.user, token)


class IsProctor(BasePermission):
    """
    Allows access only to proctor users.
    """

    def has_permission(self, request, view):
        user = request.user
        return user.is_superuser or user.permission_set.exists()