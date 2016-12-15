import pytest

from django.http import HttpResponse
from django.test import override_settings

from wagtailtrans.middleware import TranslationMiddleware
from wagtailtrans.models import Language

from tests.factories.language import LanguageFactory
from tests.factories.sites import SiteLanguagesFactory, SiteFactory


@pytest.mark.django_db
class TestTranslationMiddleware(object):

    def test_request_from_path(self, rf):
        request = rf.get('/nl/random/page/')
        TranslationMiddleware().process_request(request)

        assert request.LANGUAGE_CODE == 'nl'

    def test_request_default_language(self, rf):
        LanguageFactory(code='en', is_default=True, live=True)
        LanguageFactory(code='fr', is_default=False, live=True)

        request = rf.get('/home/')
        TranslationMiddleware().process_request(request)
        assert request.LANGUAGE_CODE == 'en'

    def test_request_site_language(self, rf):
        SiteLanguagesFactory(default_language__code='fr')

        request = rf.get('/random/page/')
        request.site = SiteFactory()
        with override_settings(WAGTAILTRANS_LANGUAGES_PER_SITE=True):
            TranslationMiddleware().process_request(request)

        assert request.LANGUAGE_CODE == 'fr'

    def test_settings_fallback(self, rf):
        Language.objects.all().delete()

        request = rf.get('/random/page/')
        with override_settings(LANGUAGE_CODE='en-us'):
            TranslationMiddleware().process_request(request)

        assert request.LANGUAGE_CODE == 'en-us'

    def test_response(self, rf):
        request = rf.get('/nl/random/page/')
        TranslationMiddleware().process_request(request)
        response = TranslationMiddleware().process_response(request, HttpResponse())
        assert response['Content-Language'] == 'nl'
