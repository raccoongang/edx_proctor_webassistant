from django.conf.urls import include, url, patterns
from rest_framework.routers import DefaultRouter
from api import views_edx
from api import views_ui

router = DefaultRouter()
router.register(r'exam_register', views_edx.ExamViewSet,
                base_name="exam-register")
router.register(r'event_session', views_ui.EventSessionViewSet,
                base_name="event-session")
router.register(r'archived_event_session',
                views_ui.ArchivedEventSessionViewSet,
                base_name="archived-event-session")
router.register(r'journaling', views_ui.JournalingViewSet,
                base_name="journaling"),
router.register(r'archived_exam', views_ui.ArchivedExamViewSet,
                base_name="archived-exam"),
router.register(r'comment', views_ui.CommentViewSet,
                base_name="comment")
router.register(r'permission', views_ui.PermissionViewSet,
                base_name="permission")

urlpatterns = patterns(
    '',
    url(r'^$', views_edx.APIRoot.as_view()),

    url(r'start_exam/(?P<attempt_code>[-\w]+)$', views_ui.start_exam,
        name='start_exam'),
    url(r'stop_exam/(?P<attempt_code>[\dA-Z\-]+)$', views_ui.stop_exam,
        name='stop_exam'),
    url(r'stop_exams/$', views_ui.stop_exams,
        name='stop_exams'),
    url(r'bulk_start_exam/$', views_ui.bulk_start_exams,
        name='bulk_start_exams'),
    url(r'poll_status/$', views_ui.poll_status,
        name='poll_status'),
    url(r'review/$', views_ui.Review.as_view(),
        name='review'),
    url(r'proctored_exams/$', views_ui.get_exams_proctored,
        name='proctor_exams'),
    url(r'comments_journaling/$', views_ui.comments_journaling,
        name='comments_journaling'),
    # url(r'bulk_review/$', views_ui.BulkReview.as_view(),
    #     name='bulk_review'),
    (r'^', include(router.urls)),

)
