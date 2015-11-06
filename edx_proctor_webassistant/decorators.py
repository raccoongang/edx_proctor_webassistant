import json
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

def set_token_cookie(view):
    """
    decorator for setting cookie with access_token, for authantification
    between backend and frontend
    """
    def wrapper(request, *args, **kwargs):
        response = view(request, *args, **kwargs)
        user = request.user
        is_auth = user.is_authenticated()
        if is_auth:
            try:
                access_token = user.social_auth.latest('pk').extra_data['access_token']
                response.set_cookie('authenticated_token',
                                    access_token,
                                    domain=settings.AUTH_SESSION_COOKIE_DOMAIN)
            except ObjectDoesNotExist:
                pass
        return response

    return wrapper