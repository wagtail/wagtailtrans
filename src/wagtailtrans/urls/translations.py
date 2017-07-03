from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from wagtail import VERSION as WAGTAIL_VERSION

if WAGTAIL_VERSION < (1, 11):
    from wagtailtrans.views.translation import (
        DeprecatedTranslationView as TranslationView
    )
else:
    from wagtailtrans.views.translation import TranslationView

app_name = 'wagtailtrans'

urlpatterns = [
    url(r'^(?P<instance_id>\d+)/add/(?P<language_code>[^/]+)/$',
        TranslationView.as_view(), name='add'),
]
