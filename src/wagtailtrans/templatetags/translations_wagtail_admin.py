from django import template

from wagtailtrans.conf import get_wagtailtrans_setting
from wagtailtrans.models import TranslatableMixin

register = template.Library()


@register.simple_tag
def get_canonical_pages_for_delete(page):
    """Get the translations made for this page

    :param page: Page instance
    :return: queryset or False
    """
    page = page.specific
    if get_wagtailtrans_setting('SYNC_TREE') and isinstance(page, TranslatableMixin) and page.is_canonical:
        return page.translations.all()

    return False
