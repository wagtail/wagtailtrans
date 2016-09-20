from django.contrib.auth.models import Group
from wagtail.wagtailcore.models import GroupPagePermission


def create_group_page_permission(page, language):
    """Create new GroupPagePermissions for
    the newly created page

    :param page: TranslatedPage instance
    :param language: Language instance
    """
    translator_perms = ['edit', 'publish']
    group, created = Group.objects.get_or_create(
        name='translator-%s' % language.code)

    for perm in translator_perms:
        GroupPagePermission.objects.create(
            group=group,
            page=page,
            permission_type=perm
        )
