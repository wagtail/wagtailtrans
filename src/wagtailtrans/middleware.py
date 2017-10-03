import re

from django import http
from django import VERSION as django_version
from django.conf import settings
from django.utils import translation

from .conf import get_wagtailtrans_setting
from .models import Language, SiteLanguages
from .sites import get_languages_for_site

if django_version >= (1, 10):
    from django.utils.deprecation import MiddlewareMixin
else:
    MiddlewareMixin = object


def _get_browser_default(site, http_accept_languages):

    # Languages from SiteSettings, rather calling manually Language Model
    # Need to change some test cases because test cases are not aware of
    # LANGUAGE_PER_SITE settings

    site_languages_codes = tuple(
        lang.code for lang in get_languages_for_site(site) if lang)

    accepted_languages = [re.split(';', language)[0]
                          for language in http_accept_languages.split(',')]

    # May i suggest a smartest way to find browser default language?
    # browser default language alwasy pass the "en-US, nl-NL"
    # Then we can search something with "-" in string

    # this is the previous code what was implemented
    for language in accepted_languages:
        default_language = (
            language if language in site_languages_codes else None)

        if default_language is None and \
                language.startswith(site_languages_codes):
            default_language = [code for code in site_languages_codes
                                if language.startswith(code)][0]

        if default_language is not None:
            break

    return default_language, site_languages_codes


def _get_redirect_url(request, active_language):
    return '/{}/'.format(active_language)


class TranslationMiddleware(MiddlewareMixin):

    def process_request(self, request):
        active_language = None

        language_from_path = translation.get_language_from_path(request.path)
        http_accept_languages = request.META.get('HTTP_ACCEPT_LANGUAGE', '')

        browser_default, language_codes = _get_browser_default(
            request.site, http_accept_languages)

        if language_from_path:
            active_language = language_from_path
        elif http_accept_languages:
            active_language = browser_default

        lang_per_site = get_wagtailtrans_setting('LANGUAGES_PER_SITE')
        redirect_to_default_lang_site = False

        # If we find default language from the url/browser, still need a
        # verification whatever it exists in CMS language setting
        if lang_per_site:
            site_languages = SiteLanguages.for_site(request.site)

            if not active_language and site_languages.default_language:
                active_language = site_languages.default_language.code

            else:
                if active_language not in language_codes \
                        and site_languages.default_language:
                    active_language = site_languages.default_language.code
                    redirect_to_default_lang_site = True

        # Still language not found in SiteSettings &| browser
        if active_language is None:
            default_language = Language.objects.default()
            if default_language:
                active_language = default_language.code
            else:
                active_language = settings.LANGUAGE_CODE

        translation.activate(active_language)
        request.LANGUAGE_CODE = active_language

        # Handling Case: Browser default language set to nl,
        # Settings set to Wagtail is language per site
        # Doesn't have the CMS language settings
        # Because routing is happening in upper layer
        if redirect_to_default_lang_site:
            redirect_url = _get_redirect_url(request, request.LANGUAGE_CODE)
            return http.HttpResponseRedirect(redirect_url)

    def process_response(self, request, response):
        if 'Content-Language' not in response:
            response['Content-Language'] = request.LANGUAGE_CODE
        return response
