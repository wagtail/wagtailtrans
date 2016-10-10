import pytest

from django.test import override_settings

from wagtailtrans.models import Language
from wagtailtrans.forms import LanguageForm

@pytest.mark.django_db
class TestLanguageForms(object):

    @override_settings(WAGTAILTRANS_SYNC_TREE=True)
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

    @override_settings(WAGTAILTRANS_SYNC_TREE=True)
    def test_post_new_default_language(self):
        Language.objects.all().delete()
        data = {
            'code': 'fr',
            'is_default': True,
            'position': 0,
            'live': True
        }
        form = LanguageForm(data)
        assert form.is_valid()
        assert not form.cleaned_data['is_default']
