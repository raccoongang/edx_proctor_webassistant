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
from django.conf.urls import include, url, patterns
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from ui.views import Index, logout
from api.views_ui import redirect_ui
from social.utils import setting_name
from social.apps.django_app.views import complete
from edx_proctor_webassistant.decorators import set_token_cookie

extra = getattr(settings, setting_name('TRAILING_SLASH'), True) and '/' or ''

urlpatterns = patterns(
    '',
    url(r'^$', Index.as_view(), name="index"),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('api.urls')),

    # few angular views
    url(r'^session/', redirect_ui),
    url(r'^archive/', redirect_ui),

    url(r'^complete/(?P<backend>[^/]+){0}$'.format(extra), set_token_cookie(complete),
        name='complete'),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(
        r'^logout/$',
        logout,
        name='logout'
    ),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
