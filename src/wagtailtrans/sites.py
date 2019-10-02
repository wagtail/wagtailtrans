from .models import SiteLanguages


def get_languages_for_site(site):
    """Utility to retrieve all available languages for site."""
    site_languages = SiteLanguages.for_site(site)
    languages = [site_languages.default_language] + list(site_languages.other_languages.all())

    return languages
