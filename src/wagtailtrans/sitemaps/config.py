from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class SitemapsAppConfig(AppConfig):
    label = 'sitemaps'
    name = 'wagtailtrans.sitemaps'
    verbose_name = _("Wagtailtrans Sitemaps")

    def ready(self):
        settings.WAGTAILSITEMAPS_GENERATOR = 'wagtailtrans.sitemaps.generator.MultilanguageSitemap'
