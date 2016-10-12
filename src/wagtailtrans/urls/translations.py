from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from wagtailtrans.views import translation

app_name = 'wagtailtrans'

urlpatterns = [
    url(r'^(?P<page_pk>\w+)/add/(?P<language_code>\w+)/$',
        translation.Add.as_view(), name='add'),
]
