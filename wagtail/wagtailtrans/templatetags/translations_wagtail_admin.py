from django import template
from django.conf import settings

from wagtail.wagtailtrans.models import TranslatedPage

register = template.Library()


@register.simple_tag
def get_canonical_pages_for_delete(page):
    """Get the translations made for this page

    :param page: Page instance
    :return: queryset or False
    """
    page = page.specific
    if (
        settings.WAGTAILTRANS_SYNC_TREE and
        getattr(page, 'language', False) and
        not page.canonical_page
    ):
        return TranslatedPage.objects.filter(canonical_page=page)
    return False
