from django.shortcuts import render
from django.views.generic import View
from api.models import Exam

class Index(View):
    template_name = 'index.html'

    def get(self, request):
        exams = Exam.objects.by_user_perms(request.user)
        return render(request, self.template_name, {'exams':exams})
