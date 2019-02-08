import pytest
from django.test import override_settings

from tests.factories.pages import ArticleFactory
from wagtailtrans.models import TranslatablePage
from wagtailtrans.wagtail_hooks import (
    edit_in_language_button, page_translations_menu)


@pytest.mark.django_db
class TestWagtailHooks:
    def setup(self):
        self.article = ArticleFactory()
        self.transpage = TranslatablePage()

    def test_edit_in_language_wagtail_hook_with_regular_page(self):
        assert list(edit_in_language_button(self.article, page_perms=[])) == []

    def test_edit_in_language_wagtail_hook_translateable_page(self):
        result = list(edit_in_language_button(self.transpage, page_perms=[]))
        assert len(result) == 1
        assert result[0].label == 'Edit in'

    def test_page_translations_menu_with_regular_page(self):
        with override_settings(WAGTAILTRANS_SYNC_TREE=False):
            assert list(page_translations_menu(self.article, page_perms=[])) == []

    def test_page_translations_menu_translateable_page(self):
        with override_settings(WAGTAILTRANS_SYNC_TREE=False):
            result = list(page_translations_menu(self.transpage, page_perms=[]))
            assert len(result) == 1
            assert result[0].label == 'Translate into'
