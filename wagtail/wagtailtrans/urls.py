
from __future__ import absolute_import, unicode_literals
from django.conf.urls import url
from wagtail.wagtailtrans.views import Index, Create, Edit, Delete

urlpatterns = [
    url(r'^$', Index.as_view(), name='index'),
    url(r'^add/$', Create.as_view(), name='add'),
    url(r'^(\d+)/$', Edit.as_view(), name='edit'),
    url(r'^(\d+)/delete/$', Delete.as_view(), name='delete'),
]
