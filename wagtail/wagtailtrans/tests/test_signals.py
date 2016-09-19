import pytest

from django.test import override_settings

from wagtail.wagtailtrans.models import TranslatedPage
from wagtail.wagtailtrans.tests import factories


@pytest.mark.django_db
class TestSignals(object):

    def setup(self):
        self.last_page = factories.create_site_tree()

    @override_settings(WAGTAILTRANS_SYNC_TREE=True)
    def test_add_language(self):
        lang = factories.LanguageFactory(is_default=False, code='fr', order=2)
        assert TranslatedPage.objects.filter(language=lang).count() == 3

    @override_settings(WAGTAILTRANS_SYNC_TREE=True)
    def test_delete_canonical_page(self):
        lang = factories.LanguageFactory(is_default=False, code='fr', order=2)
        assert TranslatedPage.objects.filter(
            language=lang, canonical_page=self.last_page).exists()
        self.last_page.delete()
        assert not TranslatedPage.objects.filter(
            language=lang, canonical_page=self.last_page).exists()
