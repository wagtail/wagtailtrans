import pytest
from wagtail.wagtailcore.models import Page

from wagtailtrans.models import Language, TranslatedPage


@pytest.fixture
def languages():
    order = 1
    for code in ['en', 'nl', 'de', 'fr']:
        Language.objects.get_or_create(
            code=code,
            is_default=True,
            order=order,
            live=True)
        order += 1


@pytest.mark.django_db
class TestLanguage(object):

    def test_create(self):
        en, created = Language.objects.get_or_create(
            code='en',
            is_default=True,
            order=1,
            live=True)
        assert isinstance(en, Language)

    def test_create_many(self, languages):
        languages = Language.objects.all()
        assert languages.count() == 4


@pytest.mark.django_db
class TestTranslatedPage(object):
    def setup(self):
        """Setup a Site root and add an english page.

        We'll use this page as canonical page throughout the tests.
        """
        en = Language.objects.get(code='en')
        self.root = Page.add_root(
            title='Site Root')
        self.root.save()
        self.canonical_page = TranslatedPage(
            slug='test-en',
            language=en,
            title='root EN'
        )
        self.root.add_child(instance=self.canonical_page)

    def test_create(self, languages):
        assert self.canonical_page.language.code == 'en'

    def test_copy_fields(self, languages):
        nl = Language.objects.get(code='nl')
        page = self._create_translation(nl, copy_fields=True)
        assert page.title

    def test_no_copy_fields(self, languages):
        nl = Language.objects.get(code='nl')
        page = self._create_translation(nl, copy_fields=False)
        assert page.title

    def test_force_parent_language(self, languages):
        en = Language.objects.get(code='en')
        nl = Language.objects.get(code='nl')
        page_nl = self._create_translation(nl, copy_fields=True)
        subpage = TranslatedPage(
            slug='sub-nl',
            language=en,
            title='Subpage in NL tree')
        assert subpage.language == en
        subpage = page_nl.add_child(instance=subpage)
        assert subpage.language == nl

    def _create_translation(self, language, copy_fields):
        new_page = self.canonical_page.create_translation(
            language=language, copy_fields=copy_fields
        )
        assert new_page.canonical_page == self.canonical_page
        return new_page
