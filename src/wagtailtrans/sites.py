from .conf import get_wagtailtrans_setting
from .models import Language, SiteLanguages


def get_languages_for_site(site):
    """Utility to retrieve available languages for provided site."""
    if get_wagtailtrans_setting('LANGUAGES_PER_SITE'):
        site_languages = SiteLanguages.for_site(site)
        languages = [site_languages.default_language] + list(site_languages.other_languages.all())
    else:
        languages = list(Language.objects.live().order_by('position'))

    return languages
