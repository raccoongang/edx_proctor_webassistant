from django.conf.urls import include, url, patterns
from rest_framework.routers import DefaultRouter
from views_edx import ExamViewSet, APIRoot
from views_ui import start_exam, poll_status

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
    (r'^', include(router.urls)),

)
