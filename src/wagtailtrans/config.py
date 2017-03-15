import logging

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger()


class WagtailTransConfig(AppConfig):
    label = 'wagtailtrans'
    name = 'wagtailtrans'
    verbose_name = _("Wagtail Translations")

    def ready(self):
        from wagtailtrans.signals import register_signal_handlers
        register_signal_handlers()
