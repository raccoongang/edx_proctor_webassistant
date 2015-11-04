from django.conf.urls import include, url, patterns
from django.views.decorators.csrf import csrf_exempt
from rest_framework.routers import DefaultRouter
from views_edx import ExamViewSet, APIRoot
from views_ui import start_exam, poll_status, review

router = DefaultRouter()
router.register(r'exam_register', ExamViewSet,
                base_name="exam-register")
#
urlpatterns = patterns(
    '',
    url(r'^$', APIRoot.as_view()),

    url(r'start_exam/(?P<attempt_code>[-\w]+)$', start_exam,
        name='start_exam'),
    url(r'poll_status/(?P<attempt_code>[-\w]+)$', poll_status,
        name='poll_status'),
    url(r'review/$', csrf_exempt(review),
        name='review'),
    (r'^', include(router.urls)),

)
