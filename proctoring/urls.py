from django.conf.urls import include, url, patterns
from proctoring import  api_edx_views,api_ui_views

urlpatterns = patterns(
    '',
    url(r'start_exam/(?P<attempt_code>[-\w]+)$', api_ui_views.start_exam,
        name='start_exam'),
    url(r'stop_exam/(?P<attempt_code>[\dA-Z\-]+)$', api_ui_views.stop_exam,
        name='stop_exam'),
    url(r'stop_exams/$', api_ui_views.stop_exams,
        name='stop_exams'),
    url(r'bulk_start_exam/$', api_ui_views.bulk_start_exams,
        name='bulk_start_exams'),
    url(r'poll_status/$', api_ui_views.poll_status,
        name='poll_status'),
    url(r'review/$', api_ui_views.Review.as_view(),
        name='review'),
    url(r'proctored_exams/$', api_ui_views.get_exams_proctored,
        name='proctor_exams'),
    url(r'comments_journaling/$', api_ui_views.comments_journaling,
        name='comments_journaling'),

)