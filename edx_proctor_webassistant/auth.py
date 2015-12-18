from rest_framework.authentication import SessionAuthentication, \
    TokenAuthentication
from rest_framework import exceptions
from rest_framework.permissions import BasePermission
from django.utils.translation import ugettext_lazy as _
from person.models import Permission
from django.conf import settings
from rest_framework.authtoken.models import Token

if settings.SSO_ENABLED:
    from social.apps.django_app.default.models import UserSocialAuth


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    Disable CSRF validation in API requests
    """
    def enforce_csrf(self, request):
        return


class SsoTokenAuthentication(TokenAuthentication):
    """
    Authentication between frontend and backend using access_token
    """
    model = UserSocialAuth if settings.SSO_ENABLED else Token

    def authenticate_credentials(self, key):
        if not settings.SSO_ENABLED:
            return super(SsoTokenAuthentication, self).authenticate_credentials(key)
        try:
            token = self.model.objects.select_related('user').get(
                extra_data={"access_token": key})
        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(
                _('User inactive or deleted.'))

        return (token.user, token)


class PermissionMixin(object):
    """
    Mixin for permissions wich checks is user proctor or instructor or student
    """
    ROLE = None

    def has_permission(self, request, view):
        user = request.user
        permissions = user.permission_set
        if self.ROLE:
            permissions = permissions.filter(
                role=self.ROLE)
        return user.is_superuser or permissions.exists()


class IsProctor(PermissionMixin, BasePermission):
    """
    Allows access only to proctor users.
    """
    ROLE = Permission.ROLE_PROCTOR


class IsInstructor(PermissionMixin, BasePermission):
    """
    Allows access only to instructor users.
    """
    ROLE = Permission.ROLE_INSTRUCTOR


class IsProctorOrInstructor(PermissionMixin, BasePermission):
    """
    Allow access to proctor or instructor
    """
    ROLE = None
