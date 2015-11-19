from django.conf.urls import include, url, patterns
from rest_framework.routers import DefaultRouter
from views_edx import ExamViewSet, APIRoot
from views_ui import (start_exam, bulk_start_exams, poll_status, get_exams_proctored,
                      Review, BulkReview, EventSessionViewSet)

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
    url(r'bulk_start_exam/(?P<attempt_codes>[-\w]+)$', bulk_start_exams,
        name='bulk_start_exams'),
    url(r'poll_status/(?P<attempt_code>[-\w]+)$', poll_status,
        name='poll_status'),
    url(r'review/$', Review.as_view(),
        name='review'),
    url(r'proctored_exams/$', get_exams_proctored,
        name='proctor_exams'),
    url(r'bulk_review/$', BulkReview.as_view(),
        name='bulk_review'),
    (r'^', include(router.urls)),

)
