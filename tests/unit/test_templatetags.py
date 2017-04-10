import pytest

from wagtailtrans.models import Language
from wagtailtrans.templatetags import wagtailtrans_tags

from tests._sandbox.pages.models import HomePage
from tests.factories.sites import create_site_tree


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
