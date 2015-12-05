from django.shortcuts import render
from django.views.generic import View


class Index(View):
    template_name = 'index.html'

    def get(self, request):
        user_has_access = request.user and request.user.is_authenticated() and request.user.permission_set.exists()
        return render(request, self.template_name, {'user_is_proctor': user_has_access})
