import pytest
from django.core.exceptions import ValidationError
from django.test import override_settings
from django.utils import six

from tests.factories.language import LanguageFactory
from tests.factories.pages import HomePageFactory, TranslatablePageFactory
from tests.factories.sites import SiteFactory, create_site_tree
from wagtailtrans import models
from wagtailtrans.exceptions import TranslationMutationError


@pytest.mark.django_db
class TestLanguage(object):

    def test_create(self):
        en, created = models.Language.objects.get_or_create(
            code='en', defaults={
                'is_default': True,
                'position': 1,
                'live': True
            })
        assert isinstance(en, models.Language)

    def test_create_many(self, languages):
        assert models.Language.objects.count() == 5

    def test_str(self):
        language = LanguageFactory()
        assert six.text_type(language) == 'British English'

    def test_default(self, languages):
        assert models.Language.objects.default().code == 'en'

    def test_has_pages_in_site(self):
        language = LanguageFactory()

        site_one = SiteFactory(
            hostname='remotehost', site_name='RemoteSite',
            root_page__title='site_1')
        site_two = SiteFactory(
            hostname='losthost', site_name='LostSite',
            root_page__title='site_2')

        create_site_tree(
            language, site=site_one, subtitle='hophop flepflep')
        create_site_tree(
            language, site=site_two, subtitle='hophop flepflep')

        language.refresh_from_db()

        assert language.has_pages_in_site(site_one)
        assert language.has_pages_in_site(site_two)


@pytest.mark.django_db
class TestTranslatablePage(object):

    def setup(self):
        """Setup a Site root and add an english page.

        We'll use this page as canonical page throughout the tests.

        """
        en = models.Language.objects.get(code='en')

        self.site_tree = create_site_tree(en)
        self.canonical_page = self.site_tree[1]

    def test_create(self):
        assert self.canonical_page.language.code == 'en'

    def test_create_translation(self, languages):
        """Test `create_translation` without copying fields."""
        nl = languages.get(code='nl')

        with override_settings(WAGTAILTRANS_SYNC_TREE=False):
            with pytest.raises(ValidationError):
                # HomePage contains some required fields which in this
                # case won't be copied, so a translation can't be made
                self.canonical_page.create_translation(language=nl)

    def test_create_translation_copy_fields(self, languages):
        """Test `create_translation` with `copy_fields` set to True."""
        nl = languages.get(code='nl')
        nl_page = self.canonical_page.create_translation(
            language=nl, copy_fields=True)

        assert nl_page.title == self.canonical_page.title
        assert nl_page.slug == '{}-{}'.format(self.canonical_page.slug, 'nl')
        assert nl_page.canonical_page == self.canonical_page
        assert nl_page.get_parent() == self.canonical_page.get_parent()

        # Other HomePage field should have been copied
        assert nl_page.subtitle == self.canonical_page.subtitle
        assert nl_page.body == self.canonical_page.body
        assert nl_page.image == self.canonical_page.image

    def test_has_translation(self, languages):
        language_nl = languages.get(code='nl')
        assert not self.canonical_page.has_translation(language_nl)
        self.canonical_page.create_translation(language_nl, copy_fields=True)
        assert self.canonical_page.has_translation(language_nl)

    def test_force_parent_language(self, languages):
        """Test `force_parent_language()`."""
        en = languages.get(code='en')
        nl = languages.get(code='nl')
        nl_page = self.canonical_page.create_translation(
            language=nl, copy_fields=True)

        subpage = TranslatablePageFactory.build(
            language=en, title='subpage in NL tree')
        assert subpage.language == en

        # After adding the English page to a Dutch tree,
        # it should have been forced into Dutch (such a wonderful world)
        nl_page.add_child(instance=subpage)
        subpage.force_parent_language()
        assert subpage.language == nl

    def test_get_translations(self, languages):
        """Test `get_translations()`."""
        nl = languages.get(code='nl')
        fr = languages.get(code='fr')

        nl_root = self.canonical_page.create_translation(
            language=nl, copy_fields=True)
        fr_root = self.canonical_page.create_translation(
            language=fr, copy_fields=True)

        # Let's only make nl_root live
        nl_root.live = True
        nl_root.save()

        en_translations = [
            p.specific for p in self.canonical_page.get_translations(
                only_live=False)]
        assert nl_root in en_translations
        assert fr_root in en_translations
        assert self.canonical_page not in en_translations

        nl_translations = [p.specific for p in nl_root.get_translations(
            only_live=False)]
        assert self.canonical_page in nl_translations
        assert fr_root in nl_translations
        assert nl_root not in nl_translations

        fr_translations = [p.specific for p in fr_root.get_translations(
            only_live=False)]
        assert self.canonical_page in fr_translations
        assert nl_root in fr_translations
        assert fr_root not in fr_translations

        # Some variations
        en_translations = [p.specific for p in self.canonical_page.get_translations()]
        assert nl_root in en_translations
        assert fr_root not in en_translations
        assert self.canonical_page not in en_translations

        en_translations = [p.specific for p in self.canonical_page.get_translations(
            include_self=True, only_live=False)]
        assert nl_root in en_translations
        assert fr_root in en_translations
        assert self.canonical_page in en_translations

    def test_move_translated_pages(self, languages):
        """Test `move_translated_pages()`."""
        en = languages.get(code='en')
        nl = languages.get(code='nl')

        # Let's first create the following structure
        #
        #    canonical_page
        #         |- subpage1
        #         |        |- leaf_page
        #         |- subpage2
        #    nl_root
        #         |- subpage1
        #         |        |- leaf_page
        #         |- subpage2

        nl_root = self.canonical_page.create_translation(
            language=nl, copy_fields=True)
        subpage1 = TranslatablePageFactory.build(
            language=en, title='subpage1 in EN tree')
        subpage2 = TranslatablePageFactory.build(
            language=en, title='subpage2 in EN tree')

        leaf_page = TranslatablePageFactory.build(
            language=en, title='leafpage in EN tree')
        self.canonical_page.add_child(instance=subpage1)
        self.canonical_page.add_child(instance=subpage2)
        subpage1.add_child(instance=leaf_page)

        nl_subpage1 = TranslatablePageFactory.build(
            language=nl, title='subpage1 in NL tree', canonical_page=subpage1)
        nl_subpage2 = TranslatablePageFactory.build(
            language=nl, title='subpage2 in NL tree', canonical_page=subpage2)
        nl_leaf_page = TranslatablePageFactory.build(
            language=nl, title='leafpage in NL tree', canonical_page=leaf_page)
        nl_root.add_child(instance=nl_subpage1)
        nl_root.add_child(instance=nl_subpage2)
        nl_subpage1.add_child(instance=nl_leaf_page)

        # Sanitiy checks
        assert len(subpage1.get_children()) == 1
        assert len(subpage2.get_children()) == 0
        assert len(nl_subpage1.get_children()) == 1
        assert len(nl_subpage2.get_children()) == 0

        def _refresh():
            subpage1.refresh_from_db()
            subpage2.refresh_from_db()
            leaf_page.refresh_from_db()
            nl_subpage1.refresh_from_db()
            nl_subpage2.refresh_from_db()
            nl_leaf_page.refresh_from_db()

        # Let's now move the leave page from subpage1 to subpage2
        # and see if the translated pages will follow
        with override_settings(WAGTAILTRANS_SYNC_TREE=False):
            leaf_page.move(subpage2, pos='last-child')
        _refresh()

        assert len(subpage1.get_children()) == 0
        assert len(subpage2.get_children()) == 1
        assert len(nl_subpage1.get_children()) == 1
        assert len(nl_subpage2.get_children()) == 0

        leaf_page.move_translated_pages(subpage2, pos='last-child')
        _refresh()

        assert len(subpage1.get_children()) == 0
        assert len(subpage2.get_children()) == 1
        assert len(nl_subpage1.get_children()) == 0
        assert len(nl_subpage2.get_children()) == 1

        # Test vice-versa, and now by just calling `move`.
        # That should trigger move_translated_pages for us
        nl_leaf_page.move(nl_subpage1, pos='last-child')
        _refresh()

        assert len(subpage1.get_children()) == 1
        assert len(subpage2.get_children()) == 0
        assert len(nl_subpage1.get_children()) == 1
        assert len(nl_subpage2.get_children()) == 0


@pytest.mark.django_db
class TestTranslatableSiteRootPage(object):

    def test_create(self):
        site_root = models.TranslatableSiteRootPage(title='site root')
        assert site_root
