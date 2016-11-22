import pytest

from wagtailtrans.models import Language
from wagtailtrans.forms import LanguageForm

from django.test import override_settings

from tests.factories import language, sites
from wagtailtrans.models import Language, SiteLanguages, TranslatablePage, register_site_languages
from wagtailtrans.signals import register_signal_handlers
from wagtailtrans.thread import set_site_languages
from wagtail.contrib.settings.views import get_setting_edit_handler
from django.forms.widgets import Select
from wagtailtrans.edit_handlers import ReadOnlyWidget

@pytest.mark.django_db
class TestLanguageForms(object):

    def test_post_first_language(self):
        Language.objects.all().delete()
        data = {
            'code': 'en',
            'is_default': True,
            'position': 0,
            'live': True
        }
        form = LanguageForm(data)
        assert form.is_valid()
        instance = form.save()
        assert instance.is_default

    def test_post_new_default_language(self):
        assert Language.objects.default()
        data = {
            'code': 'fr',
            'is_default': True,
            'position': 0,
            'live': True
        }
        form = LanguageForm(data)
        assert form.is_valid()
        assert not form.cleaned_data['is_default']
        instance = form.save()
        assert not instance.is_default


@pytest.mark.django_db
class TestSiteLanguagesAdminForm(object):

    def setup(self):
        # use a context manager to ensure these settings are
        # only used here
        with override_settings(
                WAGTAILTRANS_SYNC_TREE=True,
                WAGTAILTRANS_LANGUAGES_PER_SITE=True):
            register_site_languages()(SiteLanguages)
            self.site = sites.SiteFactory()
            set_site_languages(SiteLanguages.for_site(self.site))
            self.default_language = Language.objects.get(code='en')
            self.site.sitelanguages.default_language = self.default_language

    def test_default_language_widget(self):
        edit_handler = get_setting_edit_handler(SiteLanguages)
        form_cls = edit_handler.get_form_class(SiteLanguages)
        form = form_cls(instance=self.site.sitelanguages)
        assert isinstance(form.fields['default_language'].widget, Select)
        sites.create_site_tree(
            language=self.default_language, site=self.site)
        form = form_cls(instance=self.site.sitelanguages)
        assert isinstance(
            form.fields['default_language'].widget, ReadOnlyWidget)
