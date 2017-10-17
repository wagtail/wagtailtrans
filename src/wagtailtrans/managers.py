from django.db import models

from .conf import get_wagtailtrans_setting


class LanguageManager(models.Manager):
    """Custom manager for the `Language` model."""

    def live(self):
        """Return all the live languages."""
        return self.filter(live=True)

    def default(self, site=None):
        """Return the first choice of default languages."""

        if (
            get_wagtailtrans_setting('LANGUAGES_PER_SITE') and
            site is not None
        ):
            return site.sitelanguages.default_language

        return self.live().filter(is_default=True).first()
