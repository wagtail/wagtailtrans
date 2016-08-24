import pytest
from wagtail.wagtailtrans.models import (AbstractTranslationIndexPage,
                                         Language, TranslatedPage)


@pytest.mark.django_db
class TestAbstractTranslationIndexPage(object):

    def test_create(self):
        pass


class TestBase(object):
    def setup_languages(self):
        order = 1
        for code in ['en', 'nl', 'de', 'fr']:
            Language.objects.create(
                code=code,
                is_default=True,
                order=order,
                live=True)
            order += 1


@pytest.mark.django_db
class TestLanguage(TestBase):

    def test_create(self):
        en = Language.objects.create(
            code='en',
            is_default=True,
            order=1,
            live=True)
        assert isinstance(en, Language)

    def test_create_many(self):
        self.setup_languages()
        languages = Language.objects.all()
        assert languages.count() == 4


@pytest.mark.django_db
class TestTranslatedPage(TestBase):

    def test_create(self):
        self.setup_languages()
        language = Language.objects.get(code='en')
        root = TranslatedPage(
            language=language,
            title='root EN'
        )
        assert root.language == language

    def test_tree(self):
        self.setup_languages()
        en = Language.objects.get(code='en')
        nl = Language.objects.get(code='nl')
        page_en = TranslatedPage(
            slug='test-en',
            language=en,
            title='root EN'
        )
        page_nl = page_en.create_translation(
            language=nl
        )
        assert page_nl.canonical_page == page_en
        assert page_nl.title == page_en.title
        assert page_nl.slug == page_en.slug
