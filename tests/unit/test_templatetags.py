import pytest
from django.test import override_settings

from tests.factories.pages import WagtailPageFactory
from tests.factories.sites import SiteFactory, create_site_tree
from wagtailtrans.templatetags import (
    translations_wagtail_admin, wagtailtrans_tags)


@pytest.mark.django_db
class TestWagtailtransTags:

    def test_get_translations_util(self, languages):
        pages = create_site_tree(languages[0])
        site = pages[0].get_site()
        for language in languages[1:]:
            create_site_tree(language, site=site)

        translations = wagtailtrans_tags._get_translations(pages[1])
        language_codes = [l.code for l in translations.keys()]
        assert 'en' in language_codes
        assert 'es' in language_codes
        assert 'fr' in language_codes
        assert 'de' in language_codes
        assert 'nl' in language_codes

        translations = wagtailtrans_tags._get_translations(pages[1], include_self=False)
        language_codes = [l.code for l in translations.keys()]
        assert 'en' not in language_codes
        assert 'es' in language_codes
        assert 'fr' in language_codes
        assert 'de' in language_codes
        assert 'nl' in language_codes

    def test_get_translations(self, languages):
        site = SiteFactory()
        pages = create_site_tree(languages[0], site=site)
        for language in languages[1:]:
            create_site_tree(language, site=site)

        assert not hasattr(pages[0], 'language')
        translations = wagtailtrans_tags._get_translations(pages[0])

        language_codes = [l.code for l in translations.keys()]
        assert language_codes[0] == 'en'
        assert language_codes[1] == 'es'
        assert language_codes[2] == 'fr'
        assert language_codes[3] == 'de'
        assert language_codes[4] == 'nl'


@pytest.mark.django_db
def test_get_canonical_pages_for_delete(languages):
    page = create_site_tree(languages[0])[1]
    for lang in languages[1:]:
        page.create_translation(lang, copy_fields=True)

    canonical_pages = translations_wagtail_admin.get_canonical_pages_for_delete(page)
    assert page not in canonical_pages
    assert languages[1:].count() == canonical_pages.count()

    non_canocial_page = WagtailPageFactory(path='/root')
    assert not translations_wagtail_admin.get_canonical_pages_for_delete(non_canocial_page)

    with override_settings(WAGTAILTRANS_SYNC_TREE=False):
        assert not translations_wagtail_admin.get_canonical_pages_for_delete(page)
