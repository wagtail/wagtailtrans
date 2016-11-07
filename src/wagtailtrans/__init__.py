from os import path

from django.utils.version import get_version


VERSION = (0, 1, 0, 'final', 0)
__version__ = get_version(VERSION)

default_app_config = 'wagtailtrans.config.WagtailTransConfig'

WAGTAILTRANS_TEMPLATE_DIR = path.join(path.dirname(__file__), 'templates')
