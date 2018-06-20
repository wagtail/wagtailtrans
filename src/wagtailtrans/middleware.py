from django.conf import settings
from django.utils import translation
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import LANGUAGE_SESSION_KEY, check_for_language, get_language_from_path
from django.utils.translation.trans_real import get_languages, get_supported_language_variant

from .models import Language
from .sites import get_languages_for_site


def get_language_from_request(request):
    """
    Analyze the request to find what language the user wants the system to
    show. Only languages listed in settings.LANGUAGES are taken into account.
    If the user requests a sublanguage where we have a main language, we send
    out the main language.

    The URL path prefix will be checked for a language code.
    """
    lang_code = get_language_from_path(request.path_info)
    if lang_code is not None:
        return lang_code

    supported_lang_codes = get_languages()

    if hasattr(request, 'session'):
        lang_code = request.session.get(LANGUAGE_SESSION_KEY)
        if lang_code in supported_lang_codes and lang_code is not None and check_for_language(lang_code):
            return lang_code

    lang_code = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)

    try:
        return get_supported_language_variant(lang_code)
    except LookupError:
        return None


class TranslationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        active_language = None

        language_from_request = get_language_from_request(request)
        requested_languages = request.META.get('HTTP_ACCEPT_LANGUAGE')
        if language_from_request:
            active_language = language_from_request
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

        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME, request.LANGUAGE_CODE,
            max_age=settings.LANGUAGE_COOKIE_AGE,
            path=settings.LANGUAGE_COOKIE_PATH,
            domain=settings.LANGUAGE_COOKIE_DOMAIN,
        )
        return response
