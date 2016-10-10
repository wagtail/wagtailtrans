import pytest

from wagtailtrans.models import Language
from wagtailtrans.forms import LanguageForm

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
