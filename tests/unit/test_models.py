import pytest
from wagtail.wagtailcore.models import Page

from wagtailtrans import models




@pytest.mark.django_db
class TestLanguage(object):

    def test_create(self):
        en, created = models.Language.objects.get_or_create(code='en', defaults={
            'is_default': True,
            'position': 1,
            'live': True
        })
        assert isinstance(en, models.Language)

    def test_create_many(self, languages):
        assert models.Language.objects.count() == 5


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
        self.canonical_page = models.TranslatablePage(language=en, title='root EN')
        self.root.add_child(instance=self.canonical_page)

    def test_create(self, languages):
        assert self.canonical_page.language.code == 'en'

    def create_translation(self, languages, language, copy_fields):
        en = models.Language.objects.get(code='en')
        root = Page.add_root(title='Site Root')
        root.save()

        canonical_page = models.TranslatablePage(
            slug='test-en', language=en, title='root EN')
        root.add_child(instance=canonical_page)
        new_page = canonical_page.create_translation(
            language=language, copy_fields=copy_fields)

        assert new_page.canonical_page == canonical_page
        return new_page

    def test_copy_fields(self, languages):
        nl = models.Language.objects.get(code='nl')
        page = self._create_translation(nl, copy_fields=True)
        assert page.title

    def test_no_copy_fields(self, languages):
        nl = models.Language.objects.get(code='nl')
        page = self._create_translation(nl, copy_fields=False)
        assert page.title

    def test_force_parent_language(self, languages):
        en = models.Language.objects.get(code='en')
        nl = models.Language.objects.get(code='nl')
        page_nl = self._create_translation(nl, copy_fields=True)
        subpage = models.TranslatablePage(
            slug='sub-nl', language=en, title='Subpage in NL tree')

        assert subpage.language == en
        subpage = page_nl.add_child(instance=subpage)
        assert subpage.language == nl

    def _create_translation(self, language, copy_fields):
        new_page = self.canonical_page.create_translation(
            language=language, copy_fields=copy_fields
        )
        assert new_page.canonical_page == self.canonical_page
        return new_page



@pytest.mark.django_db
class TestTranslatableSiteRootPage(object):

    def test_create(self):
        site_root = models.TranslatableSiteRootPage(title='site root')
        assert site_root
