from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from wagtailtrans.views import translation

app_name = 'wagtailtrans'

urlpatterns = [
    url(r'^(?P<instance_id>\d+)/add/(?P<language_code>[^/]+)/$',
        translation.TranslationView.as_view(), name='add'),
]
