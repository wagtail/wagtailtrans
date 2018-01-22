from django.conf.urls import url

from wagtailtrans.views.translation import TranslationView

app_name = 'wagtailtrans'

urlpatterns = [
    url(r'^(?P<instance_id>\d+)/add/(?P<language_code>[^/]+)/$', TranslationView.as_view(), name='add'),
]
