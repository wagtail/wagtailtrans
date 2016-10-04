from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect
from django.utils.translation import activate, ugettext_lazy
from django.utils.encoding import python_2_unicode_compatible

from wagtail.utils.decorators import cached_classmethod
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, MultiFieldPanel, ObjectList, PageChooserPanel, TabbedInterface)
from wagtail.wagtailadmin.forms import WagtailAdminPageForm
from wagtail.wagtailcore.models import Page, PageManager

from .exceptions import TranslationMutationError
from .edit_handlers import ReadOnlyWidget
from .permissions import TranslatableUserPagePermissionsProxy


class LanguageManager(models.Manager):
    """Custom manager for the `Language` model."""

    def default(self):
        """Return the first choice of default languages."""
        return self.filter(live=True, is_default=True).first()


@python_2_unicode_compatible
class Language(models.Model):
    """User defined language."""

    code = models.CharField(
        max_length=12, choices=settings.LANGUAGES, unique=True,
        help_text="One of the languages defined in LANGUAGES")
    is_default = models.BooleanField(
        default=False, help_text="""
        Visitors with no language preference will see the site in
        this language
        """)
    position = models.IntegerField(
        default=0, help_text="""
        Language choices and translations will be displayed in this
        order
        """)
    live = models.BooleanField(
        default=True,
        help_text="Is this language available for visitors to view?")

    objects = LanguageManager()

    def __str__(self):
        return self.code

    class Meta:
        ordering = ['position']

    def verbose(self):
        return dict(settings.LANGUAGES).get(self.code)

    def has_pages_in_site(self, site):
        return (
            self.pages.filter(
                url_path__startswith=site.get_site_root_paths()
            ).exists())


class AdminTranslatablePageForm(WagtailAdminPageForm):
    """Form to be used in the wagtail admin."""

    def __init__(self, *args, **kwargs):
        super(AdminTranslatablePageForm, self).__init__(*args, **kwargs)
        canonical = self.initial.get('canonical_page', False)
        if settings.WAGTAILTRANS_SYNC_TREE and canonical:
            self.fields.get('language').widget = ReadOnlyWidget(
                text_display=Language.objects.get(pk=self.initial['language']))

            self.fields.get('canonical_page').widget = ReadOnlyWidget(
                text_display=TranslatablePage.objects.get(pk=canonical))

    def clean_language(self):
        return (self.instance.force_parent_language(self.parent_page) or
                Language.objects.default())


def _language_default():
    return Language.objects.default()


@python_2_unicode_compatible
class TranslatablePage(Page):
    canonical_page = models.ForeignKey(
        'self', related_name='translations', blank=True,
        null=True, on_delete=models.SET_NULL)
    language = models.ForeignKey(
        Language, related_name='pages', on_delete=models.PROTECT,
        default=_language_default)

    translation_panels = [
        MultiFieldPanel([
            FieldPanel('language'),
            PageChooserPanel('canonical_page'),
        ])
    ]

    base_form_class = AdminTranslatablePageForm

    def __str__(self):
        return "{} ({})".format(self.title, self.language)

    # def is_first_of_language(self, language):
    #     """Check if page is first of new language translation.
    #
    #     :param language: Language instance
    #     :return: Boolean
    #
    #     """
    #     site = self.get_site()
    #     translated_pages = (
    #         TranslatablePage.objects
    #         .filter(
    #             language=language,
    #             url_path__startswith=site.get_site_root_paths()
    #         ))
    #
    #     return not translated_pages.exists()

    def serve(self, request, *args, **kwargs):
        activate(self.language.code)
        return super(TranslatablePage, self).serve(request, *args, **kwargs)

    def move(self, target, pos=None, suppress_sync=False):
        """Move the page to another target.

        :param target: the new target to move the page to
        :param pos: position of the page in the new target
        :param suppress_sync: suppress syncing the translated pages
        """
        super(TranslatablePage, self).move(target, pos)

        if not suppress_sync and settings.WAGTAILTRANS_SYNC_TREE and \
           self.language.is_default:
            self.move_translated_pages(canonical_target=target, pos=pos)

    def move_translated_pages(self, canonical_target, pos=None):
        """Move only the translated pages of this instance (not self).

        This is only called when WAGTAILTRANS_SYNC_TREE is enabled

        :param canonical_target: Parent of the canonical page
        :param pos: position

        """
        translations = self.get_translations(only_live=False)
        if canonical_target.canonical_page:
            canonical_target = canonical_target.canonical_page

        for page in translations:
            # get target because at this point we assume the tree is in sync.
            target = TranslatablePage.objects.filter(
                language=page.language).filter(
                Q(canonical_page=canonical_target) | Q(pk=canonical_target.pk)
            ).get()
            page.move(target=target, pos=pos, suppress_sync=True)

    def get_translations(self, only_live=True, include_self=False):
        """Get translation of this page.

        :param only_live: Boolean to filter on live pages
        :param include_self: Should this page be part of the result set
        :return: TranslatablePage instance
        """
        canonical_page = self.canonical_page
        if not canonical_page:
            canonical_page = self

        translations = TranslatablePage.objects.filter(
            Q(canonical_page=canonical_page) |
            Q(pk=canonical_page.pk)
        )

        if only_live:
            translations = translations.filter(live=True)
        if not include_self:
            translations = translations.exclude(pk=self.pk)
        translations = translations.filter(
            language__live=True
        ).order_by('language__position')

        return translations

    def has_translation(self, language):
        """Check if page isn't already translated in given language.

        :param language: Language instance
        :return: Boolean

        """
        return (
            TranslatablePage.objects
            .filter(canonical_page=self, language=language)
            .exists())

    def get_translation_parent(self, language):
        site = self.get_site()
        if not language.has_pages_in_site(site):
            return site.root_page

        translation_parent = (
            TranslatablePage.objects
            .filter(
                canonical_page=self.get_parent(),
                language=language,
                url_path__startswith=site.get_site_root_paths()
            ).first())
        return translation_parent

    def create_translation(self, language, copy_fields=False, parent=None):
        """Create a translation for this page. If tree syncing is enabled the
        copy will also be moved to the corresponding language tree.

        :param language: Language instance
        :param copy_fields: Boolean specifying if the content should be copied
        :param parent: Parent page instance for the translation
        :return: new Translated page (or subclass) instance

        """
        if self.has_translation(language):
            raise Exception("Translation already exists")

        if not parent:
            parent = self.get_translation_parent(language)

        update_attrs = {
            'slug': '%s-%s' % (self.slug, language.code),
            'language': language,
            'live': False,
            'canonical_page': self,
        }

        if copy_fields:
            new_page = self.copy(update_attrs=update_attrs, to=parent)
        else:
            model_class = self.content_type.model_class()
            new_page = model_class(title=self.title, **update_attrs)
            parent.add_child(instance=new_page)

        return new_page

    def move_translation(self, language):
        """Place the page in the correct language tree.

        TODO: rename this method to change_language.
        However, it is being used by `signals` and there it is explicitally
        used to move the page (which is already set to the correct language) to
        the right place in the tree. We'll have to decide what
        the best design is

        :param language: the `Language` of the tree to move to
        """
        parent = self.get_parent()
        if not parent:
            raise TranslationMutationError("No parent found, don't know where "
                                           "to place the modified page.")
        parent = parent.specific

        canonical_parent = parent.canonical_page
        if not canonical_parent:
            # If None it usually means the page it self is a canonical page
            # (so part of a default language).
            # No need to check for the language being default or not, we
            # cannot do much with that information anyway
            canonical_parent = parent

        try:
            new_parent = TranslatablePage.objects.get(
                Q(canonical_page=canonical_parent) | Q(pk=canonical_parent.pk),
                language=language
            )
        except TranslatablePage.DoesNotExist:
            raise TranslationMutationError(
                "No new parent found, don't know where "
                "to place the modified page.")

        self.language = language
        self.save()
        self.move(new_parent, pos='last-child')

    def force_parent_language(self, parent=None):
        """Set Page instance language to the parent language.

        TODO: This used to be called from the `save()` method, but
        afterwards wasn't saved. Saving it would lead to recursion
        errors especially in combination with the defined signal handlers.
        We'll have to see if we can perform `force_parent_language` upon
        save (either by override `save()` or by using
        `pre_save` or `post_save` signals)

        :param parent: Parent page of self
        :return: Language instance

        """
        if not parent:
            parent = self.get_parent()

        parent = parent.specific
        if hasattr(parent, 'language'):
            if self.language != parent.language:
                self.language = parent.language
        return self.language


@cached_classmethod
def get_edit_handler(cls):
    tabs = []
    if cls.content_panels:
        tabs.append(
            ObjectList(
                cls.content_panels,
                heading=ugettext_lazy('Content')
            ))
    if cls.promote_panels:
        tabs.append(
            ObjectList(
                cls.promote_panels,
                heading=ugettext_lazy('Promote')
            ))
    if cls.settings_panels:
        tabs.append(
            ObjectList(
                cls.settings_panels,
                heading=ugettext_lazy('Settings'),
                classname='settings'
            ))
    if cls.translation_panels:
        tabs.append(
            ObjectList(
                cls.translation_panels,
                heading=ugettext_lazy('Translations')
            ))

    EditHandler = TabbedInterface(tabs, base_form_class=cls.base_form_class)
    return EditHandler.bind_to_model(cls)

TranslatablePage.get_edit_handler = get_edit_handler


def get_user_language(request):
    """Get the Language corresponding to a request.
    return default language if Language does not exist in site

    :param request: Request object
    :return: Language instance
    """
    if hasattr(request, 'LANGUAGE_CODE'):
        language = Language.objects.filter(
            code=request.LANGUAGE_CODE).first()
        if language:
            return language
    return Language.objects.default()


class TranslatableSiteRootPage(Page):
    """Root page of any translatable site.

    This page should be used as the root page because it will
    route the requests to the right language.

    """

    def serve(self, request, *args, **kwargs):
        """Serve TranslatablePage in the correct language

        :param request: request object
        :return: Http403 or Http404

        """
        language = get_user_language(request)
        candidates = TranslatablePage.objects.live().specific().child_of(self)
        try:
            translation = candidates.filter(language=language).get()
            return redirect(translation.url)
        except TranslatablePage.DoesNotExist:
            raise Http404


def page_permissions_for_user(self, user):
    """Patch for the page permissions adding our custom proxy

    Note: Since wagtail doesn't call this method on the
          specific page we need to patch the default page
          implementation for this.

    :param user: User instance
    :return: user permissions for page

    """
    user_perms = TranslatableUserPagePermissionsProxy(user)
    return user_perms.for_page(self)

Page.permissions_for_user = page_permissions_for_user
