from wagtail.wagtailtrans.tests.settings.base import *

STATIC_ROOT = '/opt/sandbox/public/static/'
MEDIA_ROOT = '/opt/sandbox/public/media/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/tmp/sandbox.sqlite3',
    }
}
