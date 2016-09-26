from django import template
from django.conf import settings

from wagtail.wagtailtrans.models import TranslatedPage

register = template.Library()


@register.simple_tag
def get_canonical_pages_count(page):
    """Get the number of translations made for this page

    :param page: Page instance
    :return: int
    """
    page = page.specific
    if (
        settings.WAGTAILTRANS_SYNC_TREE and
        getattr(page, 'language', False) and
        not page.canonical_page
    ):
        return TranslatedPage.objects.filter(canonical_page=page).all()
    return 0
