import logging

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger()


class WagtailTransConfig(AppConfig):
    label = 'wagtailtrans'
    name = 'wagtailtrans'
    verbose_name = _('Wagtail Translations')

    def ready(self):
        from django.conf import settings

        # check if WAGTAILTRANS_SYNC_TREE is set, if not use default (True)
        if not hasattr(settings, 'WAGTAILTRANS_SYNC_TREE'):
            setattr(settings, 'WAGTAILTRANS_SYNC_TREE', True)
            logger.warning(
                "Setting WAGTAILTRANS_SYNC_TREE undefined. Please specify "
                "WAGTAILTRANS_SYNC_TREE in your projects settings file.")

        from wagtailtrans.signals import register_signal_handlers
        register_signal_handlers()
