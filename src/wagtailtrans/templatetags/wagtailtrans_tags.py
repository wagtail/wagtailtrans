from collections import OrderedDict

from django.template import Library

from wagtailtrans.sites import get_languages_for_site

register = Library()


def _get_translations(page, homepage_fallback=True, include_self=True):
    """
    Return URLs for translations of provided pages, if
    a language isn't available as direct translation

    Note: after https://github.com/wagtail/wagtail/pull/3354 gets merged
          we should update the URL functions for better perfomance.

    """
    site = page.get_site()
    available_translations = {}
    available_languages = get_languages_for_site(site)
    if hasattr(page, 'language'):
        if not include_self:
            available_languages.remove(page.language)

        page_translations = page.get_translations(only_live=True, include_self=include_self)
        available_translations = {p.language.code: p for p in page_translations}

    available_homepages = {}
    if homepage_fallback:
        available_homepages = {p.language.code: p for p in site.root_page.get_children().live().specific()}

    translations = OrderedDict()
    for language in available_languages:
        translation = available_translations.get(language.code)
        if translation:
            translations[language] = translation
        elif homepage_fallback:
            homepage = available_homepages.get(language.code)
            if homepage:
                translations[language] = homepage

    return translations


@register.simple_tag
def get_translations(page, homepage_fallback=True, include_self=True):
    """Return URLs for translations of the provided page.

    Usage:
        {% get_language_urls page as language_urls %}
        {% get_language_urls page homepage_fallback=False as language_urls %}
        {% get_language_urls page homepage_fallback=False include_self=False as language_urls %}  # noqa

    """
    return _get_translations(page, homepage_fallback=homepage_fallback, include_self=include_self)


@register.inclusion_tag('wagtailtrans/templatetags/language_selector.html')
def render_language_selector(page, homepage_fallback=True, include_self=False):
    """Render language selector template with the required context.

    Usage:
        {% render_language_selector page %}
        {% render_language_selector page homepage_fallback=False %}
        {% render_language_selector page homepage_fallback=False include_self=True %}  # noqa

    """
    available_translations = _get_translations(page, homepage_fallback=homepage_fallback, include_self=include_self)

    return {
        'current_page': page,
        'translations': available_translations,
    }
