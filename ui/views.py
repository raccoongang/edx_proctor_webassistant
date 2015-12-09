import requests
import requests.cookies
from django.shortcuts import render
from django.views.generic import View
from django.conf import settings
from django.contrib.auth.views import logout


class Index(View):
    template_name = 'index.html'

    def get(self, request):
        user_has_access = request.user and request.user.is_authenticated() \
                          and request.user.permission_set.exists()
        return render(
            request,
            self.template_name,
            {'user_has_access': user_has_access}
        )


def _logout(request):
    requests.get(
        "{}/{}/".format(settings.SSO_NPOED_URL, 'logout'),
        cookies=dict(request.COOKIES)
    )
    response = logout(request=request, next_page='index')
    for key, val in dict(request.COOKIES).items():
        response.delete_cookie(key)
    domain = settings.AUTH_SESSION_COOKIE_DOMAIN
    response.set_cookie('authenticated', False, domain=domain)
    response.set_cookie('authenticated_user', 'Anonymous', domain=domain)
    response.set_cookie('authenticated_token', '', domain=domain)
    return response
