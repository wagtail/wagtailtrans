import logging

from django.conf import settings

logger = logging.getLogger(__name__)

DEFAULT_SETTINGS = {
    'SYNC_TREE': True,
    'HIDE_TRANSLATION_TREES': False,
}


def get_wagtailtrans_setting(name):
    if name == "LANGUAGES_PER_SITE":
        logger.warning("WAGTAILTRANS_LANGUAGES_PER_SITE is removed, please update your code.")
    return getattr(settings, 'WAGTAILTRANS_{}'.format(name), DEFAULT_SETTINGS[name])
