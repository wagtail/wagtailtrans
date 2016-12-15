import pytest

from django.test import Client, override_settings

from wagtailtrans.models import Language

from tests.factories.sites import SiteLanguagesFactory
from tests.factories.language import LanguageFactory


@pytest.mark.django_db
class TestTranslationMiddleware(object):

    def test_from_path(self):
        response = Client().get('http://localhost:8000/nl/random/page/')
        assert response.wsgi_request.LANGUAGE_CODE == 'nl'
        assert response['Content-Language'] == 'nl'

    def test_default_language(self):
        LanguageFactory(code='en', is_default=True, live=True)
        LanguageFactory(code='fr', is_default=False, live=True)

        response = Client().get('http://localhost:8000/home/')
        assert response.wsgi_request.LANGUAGE_CODE == 'en'
        assert response['Content-Language'] == 'en'

    def test_site_language(self):
        site_lang = SiteLanguagesFactory(default_language__code='fr')

        with override_settings(WAGTAILTRANS_LANGUAGES_PER_SITE=True):
            response = Client().get('http://localhost:8000/random/page/')

        assert response.wsgi_request.site == site_lang.site
        assert response.wsgi_request.LANGUAGE_CODE == 'fr'
        assert response['Content-Language'] == 'fr'

    def test_settings_fallback(self):
        Language.objects.all().delete()
        with override_settings(LANGUAGE_CODE='en-us'):
            response = Client().get('http://localhost:8000/random/page/')

        assert response.wsgi_request.LANGUAGE_CODE == 'en-us'
