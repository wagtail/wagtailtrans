import pytest

from django.test import override_settings

from tests.factories.pages import HomePageFactory
from wagtailtrans.models import Language, SiteLanguages, TranslatablePage
from wagtailtrans.signals import register_signal_handlers

from tests.factories import language, sites


@pytest.mark.django_db
class TestSignals(object):

    def setup(self):
        self.default_language = Language.objects.get(code='en')
        pages = sites.create_site_tree(language=self.default_language)
        self.last_page = pages[-1]

    @override_settings(WAGTAILTRANS_SYNC_TREE=True)
    def test_add_language(self):
        lang = language.LanguageFactory(
            is_default=False, code='fr', position=2)
        assert TranslatablePage.objects.filter(language=lang).count() > 1

    @override_settings(WAGTAILTRANS_SYNC_TREE=True)
    def test_delete_canonical_page(self):
        lang = language.LanguageFactory(
            is_default=False, code='fr', position=2)

        assert TranslatablePage.objects.filter(
            language=lang, canonical_page=self.last_page).exists()

        self.last_page.delete()
        assert not TranslatablePage.objects.filter(
            language=lang, canonical_page=self.last_page).exists()


@pytest.mark.django_db
class TestSignalsLanguagesPerSite(object):

    def setup(self):
        # use a context manager to ensure these settings are
        # only used here
        with override_settings(
                WAGTAILTRANS_SYNC_TREE=True,
                WAGTAILTRANS_LANGUAGES_PER_SITE=True):
            register_signal_handlers()
            self.site = sites.SiteFactory()
            SiteLanguages.for_site(self.site)
            self.default_language = Language.objects.get(code='en')
            self.site.sitelanguages.default_language = self.default_language
            pages = sites.create_site_tree(
                language=self.default_language, site=self.site)
            self.last_page = pages[-1]

    def test_add_language_to_site(self):
        with override_settings(
                WAGTAILTRANS_SYNC_TREE=True,
                WAGTAILTRANS_LANGUAGES_PER_SITE=True):
            lang = language.LanguageFactory(
                is_default=False, code='fr', position=2)
            assert not TranslatablePage.objects.filter(
                language=lang, canonical_page=self.last_page).exists()
            self.site.sitelanguages.other_languages.add(lang)
            self.site.sitelanguages.save()
            assert TranslatablePage.objects.filter(
                language=lang, canonical_page=self.last_page).exists()


@pytest.mark.django_db
class TestSignalsForceParentLanguage(object):

    def setup(self):
        with override_settings(WAGTAILTRANS_SYNC_TREE=False):
            register_signal_handlers()
            self.extra_language = language.LanguageFactory(
                code='nl', is_default=False)
            self.default_language = Language.objects.get(code='en')
            pages = sites.create_site_tree(language=self.default_language)
            self.last_page = pages[-1]

            # get trans root and add new dutch homepage
            trans_root = self.last_page.get_root_nodes().get(title='root')
            self.dutch_home = HomePageFactory.build(
                language=self.extra_language, title='dutch_homepage')
            trans_root.add_child(instance=self.dutch_home)

    def test_set_parent_language(self):
        # create new page in default language and add it to
        # the dutch homepage
        page = HomePageFactory.build(language=self.default_language)

        assert page.language == self.default_language
        assert self.dutch_home.language == self.extra_language

        page = self.dutch_home.add_child(instance=page)
        page.save()

        assert page.language == self.extra_language

