from django import VERSION as django_version
from django.conf import settings
from django.utils import translation

from .models import Language, SiteLanguages
from .utils.conf import get_wagtailtrans_setting

if django_version >= (1, 10):
    from django.utils.deprecation import MiddlewareMixin
else:
    MiddlewareMixin = object


class TranslationMiddleware(MiddlewareMixin):

    def process_request(self, request):
        language_from_path = translation.get_language_from_path(request.path)
        if language_from_path:
            active_language = language_from_path
        elif get_wagtailtrans_setting('LANGUAGES_PER_SITE') and request.site:
            site_languages = SiteLanguages.for_site(request.site)
            active_language = site_languages.default_language.code
        else:
            default_language = Language.objects.default()
            if default_language:
                active_language = default_language.code
            else:
                active_language = settings.LANGUAGE_CODE

        translation.activate(active_language)
        request.LANGUAGE_CODE = active_language

    def process_response(self, request, response):
        if 'Content-Language' not in response:
            response['Content-Language'] = request.LANGUAGE_CODE
        return response
