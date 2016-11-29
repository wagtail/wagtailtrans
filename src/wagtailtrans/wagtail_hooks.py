from django.conf.urls import include, url
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.urlresolvers import reverse
from django.utils.encoding import force_text
from django.utils.html import format_html
from wagtail.wagtailadmin import widgets
from wagtail.wagtailadmin.menu import MenuItem
from wagtail.wagtailcore import hooks

from wagtailtrans.models import Language
from wagtailtrans.urls import languages, translations
from wagtailtrans.utils.conf import get_wagtailtrans_setting


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^language/',
            include(languages, namespace='wagtailtrans_languages')),
        url(r'^translate/',
            include(translations, namespace='wagtailtrans_translations')),
    ]


@hooks.register('register_settings_menu_item')
def register_language_menu_item():
    return MenuItem(
        'Languages',
        reverse('wagtailtrans_languages:index'),
        classnames='icon icon-snippet',
        order=1000,
    )


if get_wagtailtrans_setting('LANGUAGES_PER_SITE'):
    @hooks.register('insert_global_admin_js')
    def global_admin_js():
        return format_html(
            '<script type="text/javascript" src="{path}"></script>'.format(
                path=static('wagtailtrans/js/site_languages_editor.js'))
        )


if not get_wagtailtrans_setting('SYNC_TREE'):
    """Only load hooks when WAGTAILTRANS_SYNC_TREE is disabled"""

    @hooks.register('register_page_listing_buttons')
    def page_translations_menu(page, page_perms, is_parent=False):
        if not hasattr(page, 'language'):
            return

        if hasattr(page, 'canonical_page') and page.canonical_page:
            return

        yield widgets.ButtonWithDropdownFromHook(
            'Translate into',
            hook_name='wagtailtrans_dropdown_hook',
            page=page,
            page_perms=page_perms,
            is_parent=is_parent,
            priority=10)

    @hooks.register('wagtailtrans_dropdown_hook')
    def page_translations_menu_items(page, page_perms, is_parent=False):
        prio = 1
        exclude_lang = None

        if hasattr(page, 'language') and page.language:
            exclude_lang = page.language

        other_languages = set(
            Language.objects
            .live()
            .exclude(pk=exclude_lang.pk)
            .order_by('position'))

        translations = (
            page.get_translations(only_live=False).select_related('language'))
        taken_languages = set(translations.values_list('language', flat=True))

        translation_targets = other_languages - taken_languages
        for language in translation_targets:
            yield widgets.Button(
                force_text(language),
                reverse('wagtailtrans_translations:add', kwargs={
                    'page_pk': page.pk,
                    'language_code': language.code,
                }),
                priority=prio)

            prio += 1
