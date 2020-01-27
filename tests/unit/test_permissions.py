import pytest
from django.contrib.auth.models import Permission
from django.test import override_settings

from tests.factories import sites
from tests.factories.users import UserFactory
from wagtailtrans import permissions
from wagtailtrans.models import Language


@pytest.mark.django_db
class TestTranslatableUserProxyPermission:

    def setup(self):
        self.admin_user = UserFactory(is_superuser=True)
        self.editor_user = UserFactory(first_name='Mr.XY', last_name="Z", username="translator")
        self.default_language = Language.objects.get(code='en')
        pages = sites.create_site_tree(language=self.default_language)
        self.last_page = pages[-1]
        self.site_root_page = pages[0]

    def test_admin_user_permission(self):
        permission = permissions.TranslatableUserPagePermissionsProxy(self.admin_user)
        assert permission.for_page(self.last_page).can_delete()

    def test_general_user_permission(self):
        permission = permissions.TranslatableUserPagePermissionsProxy(self.editor_user)
        assert not permission.for_page(self.last_page).can_delete()

    def test_user_permission_sync_tree(self):
        with override_settings(SYNC_TREE=True):
            permission = permissions.TranslatableUserPagePermissionsProxy(self.editor_user)
            assert not permission.for_page(self.last_page).can_delete()

    def test_create_group_page_permission(self):
        permissions.create_group_page_permission(self.last_page, self.default_language)
        group = permissions.get_or_create_language_group(self.default_language)
        permissions.create_group_permissions(group, self.default_language)

        perms = Permission.objects.get(codename='delete_translatablepage')
        self.editor_user.user_permissions.add(perms)

        permission = permissions.TranslatableUserPagePermissionsProxy(self.editor_user)
        # Only Super user can delete, Though permission has given
        assert not permission.for_page(self.last_page).can_delete()
