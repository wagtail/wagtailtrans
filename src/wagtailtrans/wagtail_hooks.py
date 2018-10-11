from django.conf.urls import include, url
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from wagtail.admin import widgets
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core import hooks
from wagtailtrans.conf import get_wagtailtrans_setting
from wagtailtrans.models import Language, TranslatablePage
from wagtailtrans.urls import translations


class LanguageModelAdmin(ModelAdmin):
    add_to_settings_menu = True
    model = Language
    menu_label = _("Languages")
    menu_icon = 'icon icon-wagtail'
    menu_order = 1000
    list_display = ['__str__', 'position', 'live', 'is_default']
    list_filter = ['live']


modeladmin_register(LanguageModelAdmin)


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^translate/', include(translations, namespace='wagtailtrans_translations')),
    ]


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
            priority=10
        )

    @hooks.register('wagtailtrans_dropdown_hook')
    def page_translations_menu_items(page, page_perms, is_parent=False):
        prio = 1
        exclude_lang = None

        if hasattr(page, 'language') and page.language:
            exclude_lang = page.language

        other_languages = set(Language.objects.live().exclude(pk=exclude_lang.pk).order_by('position'))

        translations = page.get_translations(only_live=False).select_related('language')
        taken_languages = set(t.language for t in translations)

        translation_targets = other_languages - taken_languages
        for language in translation_targets:
            yield widgets.Button(
                force_text(language),
                reverse('wagtailtrans_translations:add', kwargs={
                    'instance_id': page.pk,
                    'language_code': language.code,
                }),
                priority=prio)

            prio += 1


@hooks.register('construct_explorer_page_queryset')
def hide_non_canonical_languages(parent_page, pages, request):
    """Hide translations when WAGTAILTRANS_HIDE_TRANSLATION_TREES=True.

    This allows the user to only see the canonical language in the admin.

    """
    if parent_page.depth > 1 and get_wagtailtrans_setting('HIDE_TRANSLATION_TREES'):
        return pages.filter(
            pk__in=(
                TranslatablePage.objects
                .filter(canonical_page__isnull=True)
                .values_list('pk', flat=True)
            )
        )
    return pages


@hooks.register('register_page_listing_buttons')
def edit_in_language_button(page, page_perms, is_parent=False):
    """Add ``Edit in`` button to the page explorer.

    When hiding all other translation except the canonical language, which is
    done via ``WAGTAILTRANS_HIDE_TRANSLATION_TREES`` this will add an button to
    allow the user to select a other language to edit, which provides a more
    clear interface to work in.

    """
    if not hasattr(page, 'language'):
        return

    yield widgets.ButtonWithDropdownFromHook(
        _("Edit in"),
        hook_name='wagtailtrans_dropdown_edit_hook',
        page=page,
        page_perms=page_perms,
        is_parent=is_parent,
        priority=10
    )


@hooks.register('wagtailtrans_dropdown_edit_hook')
def edit_in_language_items(page, page_perms, is_parent=False):
    """Add all other languages in the ``Edit in`` dropdown.

    All languages other than the canonical language are listed as dropdown
    options which allows the user to click on them and edit the page in the
    language they prefer.

    """
    other_languages = (
        page.specific
        .get_translations(only_live=False)
        .exclude(pk=page.pk)
        .select_related('language')
        .order_by('language__position')
    )

    for prio, language_page in enumerate(other_languages):
        edit_url = reverse('wagtailadmin_pages:edit', args=(language_page.pk,))
        return_page = language_page.canonical_page or language_page
        next_url = reverse('wagtailadmin_explore', args=(return_page.get_parent().pk,))

        yield widgets.Button(
            force_text(language_page.language),
            "{edit_url}?next={next_url}".format(
                edit_url=edit_url,
                next_url=next_url
            ),
            priority=prio,
        )
