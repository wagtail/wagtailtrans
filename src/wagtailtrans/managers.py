from django.db import models


class LanguageManager(models.Manager):
    """Custom manager for the `Language` model."""

    def default(self):
        """Return the first choice of default languages."""
        return self.filter(live=True, is_default=True).first()
