import pytest

from wagtailtrans.templatetags import wagtailtrans_tags

from tests.factories.sites import create_site_tree, SiteFactory


@pytest.mark.django_db
class TestWagtailtransTags(object):

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

        translations = wagtailtrans_tags._get_translations(
            pages[1], include_self=False)
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
