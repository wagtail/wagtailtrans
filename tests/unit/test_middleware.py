import pytest
from django.conf import settings
from django.http import HttpResponse
from django.test import override_settings

from tests.factories.language import LanguageFactory
from tests.factories.sites import SiteFactory, SiteLanguagesFactory
from wagtailtrans.middleware import TranslationMiddleware
from wagtailtrans.models import Language


@pytest.mark.django_db
class TestTranslationMiddleware:

    def test_request_from_path(self, rf):
        request = rf.get('/nl/random/page/')
        TranslationMiddleware().process_request(request)

        assert request.LANGUAGE_CODE == 'nl'

    def test_request_default_language(self, rf):
        site = SiteFactory()
        SiteLanguagesFactory(default_language__code='fr', site=site)

        request = rf.get('/random/page/')
        request.site = site
        TranslationMiddleware().process_request(request)

        assert request.LANGUAGE_CODE == site.sitelanguages.default_language.code

    def test_settings_fallback(self, rf):
        site = SiteFactory()
        site.sitelanguages.default_language = None
        site.sitelanguages.save()

        request = rf.get('/random/page/')
        request.site = site

        with override_settings(LANGUAGE_CODE='en-us'):
            TranslationMiddleware().process_request(request)

        assert request.LANGUAGE_CODE == 'en-us'

    def test_request_language_from_header(self, rf):
        Language.objects.all().delete()
        LanguageFactory(code='en', is_default=True, live=True)
        LanguageFactory(code='fr', is_default=False, live=True)

        request = rf.get('/', HTTP_ACCEPT_LANGUAGE='fr')
        TranslationMiddleware().process_request(request)

        assert request.LANGUAGE_CODE == 'fr'

    def test_request_language_from_header_complete_match(self, rf):
        Language.objects.all().delete()
        LanguageFactory(code='en-GB', is_default=True, live=True)
        LanguageFactory(code='en-US', is_default=False, live=True)

        request = rf.get('/', HTTP_ACCEPT_LANGUAGE='en-US')
        TranslationMiddleware().process_request(request)

        assert request.LANGUAGE_CODE == 'en-US'

    def test_request_language_from_header_partial_match(self, rf):
        Language.objects.all().delete()
        LanguageFactory(code='nl', is_default=True, live=True)
        LanguageFactory(code='en', is_default=False, live=True)

        request = rf.get('/', HTTP_ACCEPT_LANGUAGE='en-GB')
        TranslationMiddleware().process_request(request)

        assert request.LANGUAGE_CODE == 'en'

    def test_request_language_from_header_multiple_first_unavailable(self, rf):
        Language.objects.all().delete()
        LanguageFactory(code='fr', is_default=True, live=True)
        LanguageFactory(code='es', is_default=False, live=True)
        languages = 'nl,en-GB;q=0.8,en;q=0.6,es-419;q=0.4,es;q=0.2'

        request = rf.get('/', HTTP_ACCEPT_LANGUAGE=languages)
        TranslationMiddleware().process_request(request)

        assert request.LANGUAGE_CODE == 'es'

    def test_response(self, rf):
        request = rf.get('/nl/random/page/')
        request.LANGUAGE_CODE = 'nl'
        response = TranslationMiddleware().process_response(request, HttpResponse())

        assert response['Content-Language'] == 'nl'

    def test_set_cookie_in_response(self, rf):
        request = rf.get('/nl/random/page/')
        request.LANGUAGE_CODE = 'nl'
        response = TranslationMiddleware().process_response(request, HttpResponse())
        assert response.cookies.get(settings.LANGUAGE_COOKIE_NAME).value == 'nl'

    def test_prefer_cookie_over_default_and_accept_header_in_request(self, rf):
        Language.objects.all().delete()
        LanguageFactory(code='en', is_default=True, live=True)
        LanguageFactory(code='fr', is_default=False, live=True)
        LanguageFactory(code='nl', is_default=False, live=True)

        request = rf.get('/', HTTP_ACCEPT_LANGUAGE='fr')
        request.COOKIES[settings.LANGUAGE_COOKIE_NAME] = 'nl'
        TranslationMiddleware().process_request(request)
        assert request.LANGUAGE_CODE == 'nl'

    def test_prefer_path_over_cookie_in_request(self, rf):
        Language.objects.all().delete()
        LanguageFactory(code='en', is_default=True, live=True)
        LanguageFactory(code='fr', is_default=False, live=True)
        LanguageFactory(code='nl', is_default=False, live=True)
        LanguageFactory(code='es', is_default=False, live=True)

        request = rf.get('/es/', HTTP_ACCEPT_LANGUAGE='fr')
        request.COOKIES[settings.LANGUAGE_COOKIE_NAME] = 'nl'
        TranslationMiddleware().process_request(request)
        assert request.LANGUAGE_CODE == 'es'
