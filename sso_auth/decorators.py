"""
Decorators for sso_auth authentication
"""
import hashlib

from social.apps.django_app.default.models import UserSocialAuth

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


def set_token_cookie(view):
    """
    decorator for setting cookie with access_token, for authentication
    between backend and frontend
    """

    def wrapper(request, *args, **kwargs):
        response = view(request, *args, **kwargs)
        user = request.user
        is_auth = user.is_authenticated()

        if not settings.SSO_ENABLED:
            response.set_cookie('authenticated', str(int(is_auth)),
                                domain=settings.AUTH_SESSION_COOKIE_DOMAIN,
                                secure=settings.SESSION_COOKIE_SECURE or None,
                                max_age=settings.SESSION_COOKIE_AGE)
            response.set_cookie('authenticated_user',
                                is_auth and user.username or 'Anonymous',
                                domain=settings.AUTH_SESSION_COOKIE_DOMAIN,
                                secure=settings.SESSION_COOKIE_SECURE or None,
                                max_age=settings.SESSION_COOKIE_AGE)

        if is_auth:
            try:
                if not settings.SSO_ENABLED:
                    str_to_hash = "%s-%s-%s" % (
                        user.username, user.email, user.last_login)
                    access_token = hashlib.md5(str_to_hash).hexdigest()
                    UserSocialAuth.objects.update_or_create(
                        provider=settings.AUTH_BACKEND_NAME,
                        uid=user.username,
                        defaults={
                            'user': user,
                            'extra_data': {'access_token': access_token}
                        }
                    )
                else:
                    access_token = user.social_auth.latest('pk').extra_data[
                        'access_token']

            except ObjectDoesNotExist:
                pass
        response.set_cookie('authenticated_token',
                            is_auth and access_token or '',
                            domain=settings.AUTH_SESSION_COOKIE_DOMAIN,
                            secure=settings.SESSION_COOKIE_SECURE or None,
                            max_age=settings.SESSION_COOKIE_AGE
                            )

        return response

    return wrapper
