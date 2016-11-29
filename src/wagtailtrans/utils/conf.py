from django.conf import settings

DEFAULT_SETTINGS = {
    'SYNC_TREE': True,
    'LANGUAGES_PER_SITE': False,
}


def get_wagtailtrans_setting(name):
    return getattr(
        settings, 'WAGTAILTRANS_{}'.format(name), DEFAULT_SETTINGS[name])
