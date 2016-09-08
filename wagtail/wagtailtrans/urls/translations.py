from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from wagtail.wagtailtrans.views import translation

urlpatterns = [
    url(r'^(?P<page>\w+)/add/(?P<language>\w+)/$',
        translation.Add.as_view(), name='add'),
]
