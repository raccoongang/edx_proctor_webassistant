from django.conf.urls import url, patterns
from proctoring import api_ui_views

urlpatterns = patterns(
    '',
    url(r'start_exam/(?P<attempt_code>[-\w]+)$', api_ui_views.StartExam.as_view(),
        name='start_exam'),
    url(r'stop_exam/(?P<attempt_code>[-\w]+)$', api_ui_views.StopExam.as_view(),
        name='stop_exam'),
    url(r'stop_exams/$', api_ui_views.StopExams.as_view(),
        name='stop_exams'),
    url(r'bulk_start_exam/$', api_ui_views.BulkStartExams.as_view(),
        name='bulk_start_exams'),
    url(r'poll_status/$', api_ui_views.PollStatus.as_view(),
        name='poll_status'),
    url(r'review/$', api_ui_views.Review.as_view(),
        name='review'),
    url(r'proctored_exams/$', api_ui_views.GetExamsProctored.as_view(),
        name='proctor_exams'),
)