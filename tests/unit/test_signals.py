import pytest
from django.test import override_settings

from tests.factories import language, sites
from wagtailtrans.models import Language, TranslatablePage


@pytest.mark.django_db
class TestSignals(object):

    def setup(self):
        self.default_language = Language.objects.get(code='en')
        pages = sites.create_site_tree(language=self.default_language)
        self.last_page = pages[-1]

    @override_settings(WAGTAILTRANS_SYNC_TREE=True)
    def test_add_language(self):
        lang = language.LanguageFactory(is_default=False, code='fr', position=2)
        assert TranslatablePage.objects.filter(language=lang).count() > 1

    @override_settings(WAGTAILTRANS_SYNC_TREE=True)
    def test_delete_canonical_page(self):
        lang = language.LanguageFactory(is_default=False, code='fr', position=2)

        assert TranslatablePage.objects.filter(
            language=lang, canonical_page=self.last_page).exists()

        self.last_page.delete()
        assert not TranslatablePage.objects.filter(
            language=lang, canonical_page=self.last_page).exists()
