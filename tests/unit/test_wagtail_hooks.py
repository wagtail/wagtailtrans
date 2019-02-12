import pytest

from wagtail.admin import widgets
from wagtail.core import hooks

from tests.factories.pages import ArticleFactory
from wagtailtrans.models import TranslatablePage
from wagtailtrans.wagtail_hooks import edit_in_language_button


@pytest.mark.django_db
class TestWagtailHooks:
    def setup(self):
        self.article = ArticleFactory()
        self.transpage = TranslatablePage()

    @hooks.register('register_page_listing_buttons')
    def page_translations_menu(self, page, page_perms, is_parent=False):
        # To test this hook i need to add it here, if we don't do this
        # we can't import the hook like the edit_in_language_button
        if not isinstance(page, TranslatablePage) or not hasattr(page, 'language'):
            return

        if hasattr(page, 'canonical_page') and page.canonical_page:
            return

        yield widgets.ButtonWithDropdownFromHook(
            'Translate into',
            hook_name='wagtailtrans_dropdown_hook',
            page=page,
            page_perms=page_perms,
            is_parent=is_parent,
            priority=10
        )

    def test_edit_in_language_wagtail_hook_with_regular_page(self):
        assert list(edit_in_language_button(self.article, page_perms=[])) == []

    def test_edit_in_language_wagtail_hook_translateable_page(self):
        result = list(edit_in_language_button(self.transpage, page_perms=[]))
        assert len(result) == 1
        assert result[0].label == 'Edit in'

    def test_page_translations_menu_with_regular_page(self):
        assert list(self.page_translations_menu(self.article, page_perms=[])) == []

    def test_page_translations_menu_translateable_page(self):
        result = list(self.page_translations_menu(self.transpage, page_perms=[]))
        assert len(result) == 1
        assert result[0].label == 'Translate into'
