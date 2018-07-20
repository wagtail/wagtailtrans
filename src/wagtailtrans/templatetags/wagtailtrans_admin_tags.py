from django import template

from wagtailtrans.conf import get_wagtailtrans_setting
from wagtailtrans.models import Language, TranslatablePage

register = template.Library()


@register.simple_tag
def get_canonical_pages_for_delete(page):
    """Get the translations made for this page

    :param page: Page instance
    :return: queryset or False
    """
    page = page.specific
    if get_wagtailtrans_setting('SYNC_TREE') and getattr(page, 'language', False) and not page.canonical_page:
        return TranslatablePage.objects.filter(canonical_page=page)
    return False


@register.simple_tag
def get_related_pages_for_language(language):
    """Get the TranslatablePages for this Language

    :param language: Language instance
    :return: queryset or False
    """
    if isinstance(language, Language):
        pages = language.pages.all()
        for page in pages:
            if page.is_canonical:
                translated_pages = page.get_translations()
                pages = pages.union(translated_pages)
        return pages.order_by("title")
    return False
