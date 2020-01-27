import pytest
from django.test import override_settings

from tests.factories import language, sites
from tests.factories.pages import HomePageFactory, WagtailPageFactory
from wagtailtrans import signals
from wagtailtrans.models import Language, SiteLanguages, TranslatablePage
from wagtailtrans.signals import register_signal_handlers


@pytest.mark.django_db
class TestSignals:

    def setup(self):
        self.default_language = Language.objects.get(code='en')
        pages = sites.create_site_tree(language=self.default_language)
        self.last_page = pages[-1]

    @override_settings(WAGTAILTRANS_SYNC_TREE=True)
    def test_add_language(self):
        lang = language.LanguageFactory(is_default=False, code='fr', position=2)
        assert TranslatablePage.objects.filter(language=lang).count() > 1

    @override_settings(WAGTAILTRANS_SYNC_TREE=True)
    def test_delete_canonical_page(self):
        lang = language.LanguageFactory(is_default=False, code='fr', position=2)

        assert TranslatablePage.objects.filter(language=lang, canonical_page=self.last_page).exists()

        self.last_page.delete()
        assert not TranslatablePage.objects.filter(language=lang, canonical_page=self.last_page).exists()

    @override_settings(WAGTAILTRANS_SYNC_TREE=True)
    def test_do_not_copy_non_translatable_page(self):
        page = WagtailPageFactory.build(title='test')
        self.last_page.add_child(instance=page)
        lang = language.LanguageFactory(is_default=False, code='fr', position=2)

        assert TranslatablePage.objects.filter(language=lang, canonical_page=self.last_page).exists()


@pytest.mark.django_db
class TestSignalsLanguagesPerSite:

    def setup(self):
        # use a context manager to ensure these settings are
        # only used here
        with override_settings(WAGTAILTRANS_SYNC_TREE=True, WAGTAILTRANS_LANGUAGES_PER_SITE=True):
            register_signal_handlers()
            self.site = sites.SiteFactory()
            SiteLanguages.for_site(self.site)
            self.default_language = Language.objects.get(code='en')
            self.site.sitelanguages.default_language = self.default_language
            pages = sites.create_site_tree(language=self.default_language, site=self.site)
            self.last_page = pages[-1]

    def test_add_language_to_site(self):
        with override_settings(WAGTAILTRANS_SYNC_TREE=True, WAGTAILTRANS_LANGUAGES_PER_SITE=True):
            lang = language.LanguageFactory(is_default=False, code='fr', position=2)
            assert not TranslatablePage.objects.filter(language=lang, canonical_page=self.last_page).exists()
            self.site.sitelanguages.other_languages.add(lang)
            self.site.sitelanguages.save()
            assert TranslatablePage.objects.filter(language=lang, canonical_page=self.last_page).exists()


@pytest.mark.django_db
class TestForceParentLanguage:

    def test_parent_language(self):
        parent_page = HomePageFactory.build()
        new_page = HomePageFactory.build(language=language.LanguageFactory(code='ar'))

        signals.force_parent_language(page=new_page, parent=parent_page)
        assert new_page.language == parent_page.language

    @override_settings(WAGTAILTRANS_LANGUAGES_PER_SITE=True)
    def test_site_languages(self):
        site = sites.SiteFactory()
        SiteLanguages.for_site(site)  # Initialize sitelanguages

        default_language = Language.objects.default()
        lang = language.LanguageFactory(code='nl', is_default=False)
        site.sitelanguages.default_language = lang
        site.sitelanguages.save()

        pages = sites.create_site_tree(language=default_language, site=site)
        homepage = HomePageFactory.build(language=default_language)
        pages[0].add_child(instance=homepage)

        signals.force_parent_language(page=homepage, parent=site.root_page)

        assert homepage.language == lang
