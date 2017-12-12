import pytest

from tests.factories.pages import TranslatablePageFactory
from tests.factories.sites import create_site_tree
from wagtailtrans import models
from wagtailtrans.utils.language_switch import change_default_language


@pytest.mark.django_db
class TestTranslatablePage(object):

    def setup(self):
        """Setup a Site root and add an english page.
        """
        en = models.Language.objects.get(code='en')
        en.is_default = True
        self.site_tree = create_site_tree(en)
        self.canonical_page = self.site_tree[1]

    def test_switch_new_language(self, languages):

        en = languages.get(code='en')
        nl = languages.get(code='nl')

        nl_root = self.canonical_page.create_translation(
            language=nl, copy_fields=True)
        subpage1 = TranslatablePageFactory.build(
            language=en, title='subpage1 in EN tree')
        subpage2 = TranslatablePageFactory.build(
            language=en, title='subpage2 in EN tree')

        self.canonical_page.add_child(instance=subpage1)
        self.canonical_page.add_child(instance=subpage2)

        TranslatablePageFactory.build(
            language=nl, title='subpage1 in NL tree', canonical_page=subpage1)
        TranslatablePageFactory.build(
            language=nl, title='subpage2 in NL tree', canonical_page=subpage2)

        change_default_language(nl)

        assert nl.is_default
        assert models.TranslatablePage.objects.filter(
            language=en).first().canonical_page.language == nl
        assert models.TranslatablePage.objects.filter(
            language=nl).first().canonical_page is None
