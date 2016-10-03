import pytest
from django.db import transaction
from django.test import override_settings
from wagtail.wagtailcore.models import Page

from wagtailtrans import models
from tests.factories.language import LanguageFactory
from tests.factories.pages import TranslatablePageFactory
from tests.factories.sites import create_site_tree, SiteFactory


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

    def test_verbose(self):
        language = LanguageFactory()
        assert language.verbose() == 'British English'


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

    @override_settings(WAGTAILTRANS_SYNC_TREE=False)
    def test_create_translation(self):
        language = LanguageFactory(code='br')
        new_page = self.canonical_page.create_translation(
            language=language, copy_fields=True)

        assert new_page.canonical_page == self.canonical_page
        assert new_page.language.code == 'br'

    # @override_settings(WAGTAILTRANS_SYNC_TREE=False)
    # def teste_copy_fields(self):
    #     nl = models.Language.obejcts.get(code='nl')

    @override_settings(WAGTAILTRANS_SYNC_TREE=False)
    def test_is_first_of_language(self):
        language = models.Language.objects.get(code='en')
        language_es = LanguageFactory(code='es')
        site = SiteFactory(
            hostname='remotehost', port=80, site_name='RemoteTestSite',
            is_default_site=False, root_page__title='trans-site-root-es')
        page_tree = create_site_tree(language, site)
        subpage = page_tree.pop()
        assert subpage.is_first_of_language(language_es)

    @override_settings(WAGTAILTRANS_SYNC_TREE=False)
    def test_is_not_first_of_language(self):
        language = models.Language.objects.get(code='en')
        language_es = LanguageFactory(code='es')
        site = SiteFactory(
            hostname='remotehost', port=80, site_name='RemoteTestSite',
            is_default_site=False, root_page__title='trans-site-root-es')
        page_tree = create_site_tree(language, site)
        page_tree[1].add_child(title='es-home', language=language_es)
        assert page_tree.pop().is_first_of_language(language_es)


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
