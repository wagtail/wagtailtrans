
from django.conf.urls import include, url
from django.core import urlresolvers
from wagtail.wagtailadmin.menu import MenuItem
from wagtail.wagtailadmin import widgets
from wagtail.wagtailcore import hooks
from wagtail.wagtailtrans import urls


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^language/', include(
            urls, app_name='wagtailtrans',
            namespace='wagtailtrans_languages')),
    ]


@hooks.register('register_settings_menu_item')
def register_language_menu_item():
    return MenuItem(
        'Languages',
        urlresolvers.reverse('wagtailtrans_languages:index'),
        classnames='icon icon-snippet',
        order=1000,
    )


@hooks.register('register_page_listing_buttons')
def page_translations_menu(page, page_perms, is_parent=False):
    yield widgets.PageListingButton(
        'translations',
        '/some/url',
        priority=10)
