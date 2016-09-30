import pytest
from django.core.exceptions import ValidationError
from wagtail.wagtailcore.models import Page

from tests.factories.language import LanguageFactory
from tests.factories.pages import HomePageFactory, TranslatedPageFactory
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

    def test_verbose(self):
        language = LanguageFactory()
        assert language.verbose() == 'British English'

    def test_default(self, languages):
        assert models.Language.objects.default().code == 'en'


@pytest.mark.django_db
class TestTranslatablePage(object):
    def setup(self):
        """Setup a Site root and add an english page.

        We'll use this page as canonical page throughout the tests.

        """
        en = models.Language.objects.get(code='en')
        self.root = Page.add_root(
            title='Site Root')
        self.root.save()
        self.en_root = HomePageFactory.build(language=en)
        self.root.add_child(instance=self.en_root)

    def test_create(self, languages):
        """Test some basic attributes of the `TranslatablePage`."""
        assert self.en_root.language.code == 'en'

    def test_create_translation(self, languages):
        """Test `create_translation` without copying fields."""
        nl = languages.get(code='nl')

        with pytest.raises(ValidationError):
            # HomePage contains some required fields which in this
            # case won't be copied, so a translation can't be made
            self.en_root.create_translation(language=nl)

    def test_create_translation_copy_fields(self, languages):
        """Test `create_translation` with `copy_fields` set to True."""
        nl = languages.get(code='nl')
        nl_page = self.en_root.create_translation(language=nl,
                                                  copy_fields=True)

        assert nl_page.title == self.en_root.title
        assert nl_page.slug == "{}-{}".format(self.en_root.slug, 'nl')
        assert nl_page.canonical_page == self.en_root
        assert nl_page.get_parent() == self.en_root.get_parent()

        # Other HomePage field should have been copied
        assert nl_page.subtitle == self.en_root.subtitle
        assert nl_page.body == self.en_root.body
        assert nl_page.image == self.en_root.image

    def test_force_parent_language(self, languages):
        """Test `force_parent_language()`."""
        en = languages.get(code='en')
        nl = languages.get(code='nl')
        nl_page = self.en_root.create_translation(language=nl,
                                                  copy_fields=True)

        subpage = TranslatedPageFactory.build(language=en,
                                              title='subpage in NL tree')
        assert subpage.language == en

        # After adding the English page to a Dutch tree,
        # it should have been forced into Dutch (such a wonderful world)
        nl_page.add_child(instance=subpage)
        subpage.force_parent_language()
        assert subpage.language == nl

    def test_move_translation(self, languages):
        """Test `move_translation()`."""
        en = languages.get(code='en')
        nl = languages.get(code='nl')

        subpage = TranslatedPageFactory.build(language=en,
                                              title='subpage in EN tree')
        self.en_root.add_child(instance=subpage)
        nl_root = HomePageFactory.build(language=nl)
        self.root.add_child(instance=nl_root)

        # Some sanity checks
        assert len(self.en_root.get_children()) == 1
        assert len(nl_root.get_children()) == 0

        # nl_root and en_root are not linked yet, so it will raise an error
        with pytest.raises(TranslationMutationError):
            subpage.move_translation(nl)

        nl_root.canonical_page = self.en_root
        nl_root.save()

        # It should succeed now
        subpage.move_translation(nl)
        subpage_pk = subpage.pk  # store for later checking

        self.en_root.refresh_from_db()
        nl_root.refresh_from_db()

        assert len(self.en_root.get_children()) == 0
        assert len(nl_root.get_children()) == 1
        subpage = nl_root.get_children()[0].specific
        assert subpage.pk == subpage_pk
        assert subpage.language == nl

        # Other way around again.
        # We'll test this because en_root is the canonical page of nl_root
        # but not the other way around. It should be able to move
        # it correctly even in this case
        subpage.move_translation(en)
        self.en_root.refresh_from_db()
        nl_root.refresh_from_db()

        assert len(self.en_root.get_children()) == 1
        assert len(nl_root.get_children()) == 0
        subpage = self.en_root.get_children()[0].specific
        assert subpage.pk == subpage_pk
        assert subpage.language == en

    def test_is_first_of_language(self, languages):
        """Test `is_first_of_language()`."""
        en = languages.get(code='en')
        assert self.en_root.is_first_of_language()
        subpage = TranslatedPageFactory.build(language=en,
                                              title='subpage in EN tree')
        self.en_root.add_child(instance=subpage)

        assert not subpage.is_first_of_language()
        assert not self.en_root.is_first_of_language()


@pytest.mark.django_db
class TestTranslatableSiteRootPage(object):

    def test_create(self):
        site_root = models.TranslatableSiteRootPage(title='site root')
        assert site_root
