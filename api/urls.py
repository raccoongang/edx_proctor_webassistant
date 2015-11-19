from django.conf.urls import include, url, patterns
from rest_framework.routers import DefaultRouter
from views_edx import ExamViewSet, APIRoot
from views_ui import start_exam, poll_status, get_exams_proctored, \
    Review, EventSessionViewSet

router = DefaultRouter()
router.register(r'exam_register', ExamViewSet,
                base_name="exam-register")
router.register(r'event_session', EventSessionViewSet,
                base_name="event-session")
#
urlpatterns = patterns(
    '',
    url(r'^$', APIRoot.as_view()),

    url(r'start_exam/(?P<attempt_code>[-\w]+)$', start_exam,
        name='start_exam'),
    url(r'poll_status/(?P<attempt_code>[-\w]+)$', poll_status,
        name='poll_status'),
    url(r'review/$', Review.as_view(),
        name='review'),
    url(r'proctored_exams/$', get_exams_proctored,
        name='proctor_exams'),
    (r'^', include(router.urls)),

)
