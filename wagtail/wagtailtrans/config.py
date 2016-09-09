from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _


class WagtailTransConfig(AppConfig):
    label = 'wagtailtrans'
    name = 'wagtail.wagtailtrans'
    verbose_name = _('Wagtail Translations')

    def ready(self):
        from wagtail.wagtailtrans.signals import register_signal_handlers
        register_signal_handlers()

        from django.conf import settings
        if not hasattr(settings, 'WAGTAILTRANS_SYNC_TREE'):
            raise ImproperlyConfigured(
                "Setting WAGTAILTRANS_SYNC_TREE undefined. Please specify "
                "WAGTAILTRANS_SYNC_TREE in your projects settings file.")
