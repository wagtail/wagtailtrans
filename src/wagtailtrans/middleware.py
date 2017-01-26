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
        active_language = None
        language_from_path = translation.get_language_from_path(request.path)
        requested_languages = request.META.get('HTTP_ACCEPT_LANGUAGE')
        if language_from_path:
            active_language = language_from_path
        elif requested_languages:
            requested_languages = requested_languages.split(',')
            codes = tuple(
                Language.objects.live().values_list('code', flat=True))
            for language in requested_languages:
                language = language.split(';')[0]
                active_language = (
                    language if language in codes else None)
                if active_language is None and language.startswith(codes):
                    active_language = [
                        code for code in codes
                        if language.startswith(code)][0]
                if active_language is not None:
                    break

        lang_per_site = get_wagtailtrans_setting('LANGUAGES_PER_SITE')
        if active_language is None and lang_per_site and request.site:
            site_languages = SiteLanguages.for_site(request.site)
            if site_languages.default_language:
                active_language = site_languages.default_language.code

        if active_language is None:
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
