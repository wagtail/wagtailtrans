from django.conf import settings
from django.utils import translation
from django.utils.deprecation import MiddlewareMixin

from .models import Language
from .sites import get_languages_for_site


class TranslationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        active_language = None
        language_from_path = translation.get_language_from_path(request.path)
        requested_languages = request.META.get('HTTP_ACCEPT_LANGUAGE')
        if language_from_path:
            active_language = language_from_path
        elif requested_languages:
            requested_languages = requested_languages.split(',')
            codes = tuple(language.code for language in get_languages_for_site(request.site) if language)

            for language in requested_languages:
                language = language.split(';')[0]
                active_language = language if language in codes else None

                if active_language is None and language.startswith(codes):
                    active_language = [c for c in codes if language.startswith(c)][0]
                if active_language is not None:
                    break

        if active_language is None:
            default_language = Language.objects.default_for_site(site=request.site)

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
