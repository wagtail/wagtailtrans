from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from wagtailtrans.views import language

app_name = 'wagtailtrans'

urlpatterns = [
    url(r'^$', language.Index.as_view(), name='index'),
    url(r'^add/$', language.Create.as_view(), name='add'),
    url(r'^(\d+)/$', language.Edit.as_view(), name='edit'),
    url(r'^(\d+)/delete/$', language.Delete.as_view(), name='delete'),
]
