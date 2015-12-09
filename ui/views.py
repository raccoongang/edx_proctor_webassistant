import requests
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
    requests.get("{}/{}/".format(settings.SSO_NPOED_URL, 'logout'))
    response = logout(request=request, next_page='index')
    for key, val in request.COOKIES.items():
        response.delete_cookie(key)
    return response
