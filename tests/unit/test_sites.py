import pytest
from django.test import override_settings

from wagtailtrans import sites

from tests.factories.sites import SiteFactory, SiteLanguagesFactory


@pytest.mark.django_db
def test_get_languages_for_site(languages):
    site = SiteFactory()
    languages = sites.get_languages_for_site(site)

    language_codes = [l.code for l in languages]
    assert language_codes == ['en', 'es', 'fr', 'de', 'nl']

    site_lang = SiteLanguagesFactory(site=site, default_language=languages[0])
    site_lang.other_languages.add(languages[1], languages[2])

    with override_settings(WAGTAILTRANS_LANGUAGES_PER_SITE=True):
        language_codes = [l.code for l in sites.get_languages_for_site(site)]
        assert language_codes == ['en', 'es', 'fr']

