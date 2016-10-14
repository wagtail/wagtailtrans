from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from wagtailtrans.views import translation

app_name = 'wagtailtrans'

urlpatterns = [
    url(r'^(?P<page_pk>\d+)/add/(?P<language_code>[^/]+)/$',
        translation.Add.as_view(), name='add'),
]
