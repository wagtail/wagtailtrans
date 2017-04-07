from django import VERSION as django_version
from django.template import Library

from wagtailtrans.sites import get_languages_for_site

register = Library()

if django_version >= (1, 9):
    register.assignment_tag = register.simple_tag


def _get_language_urls(page, homepage_fallback=True):
    """
    Return URLs for translations of provided pages, if
    a language isn't available as direct translation

    Note: after https://github.com/wagtail/wagtail/pull/3354 gets merged
          we should update the URL functions for better perfomance.

    """
    site = page.get_site()
    available_languages = get_languages_for_site(site)
    available_translations = {
        p.language.code: p
        for p in page.get_translations(only_live=True, include_self=True)
    }

    available_homepages = {}
    if homepage_fallback:
        available_homepages = {
            p.language.code: p for p in site.root_page.get_children()
        }

    language_urls = {}
    for language in available_languages:
        translation = available_translations.get(language.code)
        if translation:
            language_urls[language.code] = translation.url
        elif homepage_fallback:
            homepage = available_homepages.get(language.code)
            if homepage:
                language_urls[language.code] = homepage.url

    return language_urls


@register.assignment_tag
def get_translation_urls(page, homepage_fallback=True):
    """Return URLs for translations of the provided page.

    Usage:
        {% get_language_urls page as language_urls %}

        {% get_language_urls page False as language_urls %}

    """
    return _get_language_urls(page, homepage_fallback=homepage_fallback)


@register.inclusion_tag('wagtailtrans/templatetags/language_selector.html')
def render_language_selector(page, homepage_fallback=True):
    """Render language selector template with the required context.

    Usage:
        {% render_language_selector page %}

        {% render_language_selector page False%}

    """
    available_urls = _get_language_urls(page, homepage_fallback=homepage_fallback)
    return {
        'current_page': page,
        'language_urls': available_urls,
    }
