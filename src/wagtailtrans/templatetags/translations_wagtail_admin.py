import django
from django import template

from wagtailtrans.models import TranslatablePage
from wagtailtrans.utils.conf import get_wagtailtrans_setting

register = template.Library()


if django.VERSION >= (1, 9):
    assignment_tag = register.simple_tag
else:
    assignment_tag = register.assignment_tag


@assignment_tag
def get_canonical_pages_for_delete(page):
    """Get the translations made for this page

    :param page: Page instance
    :return: queryset or False
    """
    page = page.specific
    if (
        get_wagtailtrans_setting('SYNC_TREE') and
        getattr(page, 'language', False) and
        not page.canonical_page
    ):
        return TranslatablePage.objects.filter(canonical_page=page)
    return False


@assignment_tag
def languages_per_site_enabled():
    return get_wagtailtrans_setting('LANGUAGES_PER_SITE')
