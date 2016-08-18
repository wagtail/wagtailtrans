
from django.conf.urls import include, url
from django.core import urlresolvers
from wagtail.wagtailadmin.menu import MenuItem
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
