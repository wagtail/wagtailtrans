from django.db import models


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
        return self.filter(site_default_language__site=site).first()
