import pytest
from django.test import override_settings

from wagtailtrans.models import TranslatedPage

from tests.factories import sites, language


@pytest.mark.django_db
class TestSignals(object):

    def setup(self):
        self.last_page = sites.create_site_tree()

    @override_settings(WAGTAILTRANS_SYNC_TREE=True)
    def test_add_language(self):
        lang = language.LanguageFactory(is_default=False, code='fr', position=2)
        assert TranslatedPage.objects.filter(language=lang).count() > 1

    @override_settings(WAGTAILTRANS_SYNC_TREE=True)
    def test_delete_canonical_page(self):
        lang = language.LanguageFactory(is_default=False, code='fr', position=2)

        assert TranslatedPage.objects.filter(
            language=lang, canonical_page=self.last_page).exists()

        self.last_page.delete()
        assert not TranslatedPage.objects.filter(
            language=lang, canonical_page=self.last_page).exists()
