from django.db import models

from .conf import get_wagtailtrans_setting


class LanguageManager(models.Manager):
    """Custom manager for the `Language` model."""

    def live(self):
        """Return all the live languages."""
        return self.filter(live=True)

    def default(self):
        """Return the first choice of default languages."""
        return self.live().filter(is_default=True).first()

    def default_for_site(self, site):
        """Return default language for site"""
        if get_wagtailtrans_setting('LANGUAGES_PER_SITE'):
            return self.filter(site_default_language__site=site).first()
        return self.default()
