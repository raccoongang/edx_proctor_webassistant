import hashlib
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from social.apps.django_app.default.models import UserSocialAuth


def set_token_cookie(view):
    """
    decorator for setting cookie with access_token, for authentication
    between backend and frontend
    """

    def wrapper(request, *args, **kwargs):
        response = view(request, *args, **kwargs)
        user = request.user
        is_auth = user.is_authenticated()
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

                response.set_cookie('authenticated_token',
                                    access_token,
                                    domain=settings.AUTH_SESSION_COOKIE_DOMAIN
                                    )
            except ObjectDoesNotExist:
                pass
        return response

    return wrapper
