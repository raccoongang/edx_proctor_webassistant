"""edx_proctor_webassistant URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf import settings
from django.conf.urls import include, url, patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from social.apps.django_app.views import complete
from social.utils import setting_name

from journaling.api_views import JournalingViewSet
from person.api_views import PermissionViewSet
from proctoring import api_edx_views, api_ui_views
from sso_auth.decorators import set_token_cookie
from ui.views import Index, logout,login as login_view

router = DefaultRouter()
router.register(r'exam_register', api_edx_views.ExamViewSet,
                base_name="exam-register")
router.register(r'event_session', api_ui_views.EventSessionViewSet,
                base_name="event-session")
router.register(r'archived_event_session',
                api_ui_views.ArchivedEventSessionViewSet,
                base_name="archived-event-session")
router.register(r'journaling', JournalingViewSet,
                base_name="journaling"),
router.register(r'archived_exam', api_ui_views.ArchivedExamViewSet,
                base_name="archived-exam"),
router.register(r'comment', api_ui_views.CommentViewSet,
                base_name="comment")
router.register(r'permission', PermissionViewSet,
                base_name="permission")

urlpatterns = patterns(
    '',
    url(r'^$', Index.as_view(), name="index"),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/$', api_edx_views.APIRoot.as_view()),
    (r'^api/', include('proctoring.urls')),
    (r'^api/', include(router.urls)),
    # few angular views
    url(r'^session/', api_ui_views.redirect_ui),
    url(r'^archive/', api_ui_views.redirect_ui),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if not settings.SSO_ENABLED:
    urlpatterns += [
        url(r'^login/$', set_token_cookie(login_view), name='login'),
        url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout')
    ]
else:
    extra = getattr(settings, setting_name('TRAILING_SLASH'),True) and '/' or ''
    urlpatterns += [
        url(r'^complete/(?P<backend>[^/]+){0}$'.format(extra),
            set_token_cookie(complete), name='complete'),
        url('', include('social.apps.django_app.urls', namespace='social')),
        url(r'^logout/$', logout, name='logout'),
    ]
