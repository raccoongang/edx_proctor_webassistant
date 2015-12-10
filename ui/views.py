from django.shortcuts import render
from django.views.generic import View
from django.conf import settings
# from django.contrib.auth.views import logout
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import redirect


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


def logout(request, next_page=None,
           redirect_field_name=REDIRECT_FIELD_NAME, *args, **kwargs):
    """
    This view needed for correct redirect to sso-logout page
    """
    if (redirect_field_name in request.POST or
            redirect_field_name in request.GET):
        next_page = request.POST.get(redirect_field_name,
                                     request.GET.get(redirect_field_name))

    if next_page:
        next_page = request.build_absolute_uri(next_page)
    else:
        next_page = request.build_absolute_uri('/')

    return redirect('%s?%s=%s' % (settings.SSO_NPOED_URL + "/logout",
                                      redirect_field_name, next_page))
