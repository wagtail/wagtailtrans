from django.conf import settings
from django.contrib.auth.models import Group
from wagtail.wagtailcore.models import (
    GroupPagePermission, UserPagePermissionsProxy, PagePermissionTester)


def get_or_create_language_group(language):
    """Create new translator group for language

    :param language: Language instance
    :return: Group
    """
    group, created = Group.objects.get_or_create(
        name='translator-%s' % language.code)
    return group


def create_group_page_permission(page, language):
    """Create new GroupPagePermissions for
    the newly created page

    :param page: TranslatedPage instance
    :param language: Language instance
    """
    translator_perms = ['edit', 'publish']
    group = get_or_create_language_group(language)

    for perm in translator_perms:
        GroupPagePermission.objects.create(
            group=group,
            page=page,
            permission_type=perm
        )


class TranslatablePagePermissionsTester(PagePermissionTester):

    def can_delete(self):
        has_canonical = getattr(self.page.specific, 'canonical_page', False)
        if has_canonical and settings.WAGTAILTRANS_SYNC_TREE:
            return False
        return super(TranslatablePagePermissionsTester, self).can_delete()


class TranslatableUserPagePermissionProxy(UserPagePermissionsProxy):

    def for_page(self, page):
        return TranslatablePagePermissionsTester(self, page)
