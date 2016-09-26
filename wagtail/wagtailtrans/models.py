from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect
from django.utils.translation import activate, ugettext_lazy

from wagtail.utils.decorators import cached_classmethod
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, MultiFieldPanel, ObjectList, PageChooserPanel, TabbedInterface)
from wagtail.wagtailadmin.forms import WagtailAdminPageForm
from wagtail.wagtailcore.models import Page

from wagtail.wagtailtrans.permissions import (
    create_group_page_permission, TranslatableUserPagePermissionsProxy)


class Language(models.Model):
    code = models.CharField(
        max_length=12,
        help_text="One of the languages defined in LANGUAGES",
        choices=settings.LANGUAGES,
        unique=True,
    )

    is_default = models.BooleanField(
        default=False, help_text="""
        Visitors with no language preference will see the site in
        this language
        """)

    order = models.IntegerField(
        help_text="""
        Language choices and translations will be displayed in this
        order
        """)

    live = models.BooleanField(
        default=True,
        help_text="Is this language available for visitors to view?"
    )

    def __str__(self):
        return self.code

    class Meta:
        ordering = ['order']

    def verbose(self):
        return [x for x in settings.LANGUAGES if x[0] == self.code][0][1]


def get_default_language():
    return Language.objects.filter(live=True, is_default=True).first()


class AdminTranslatedPageForm(WagtailAdminPageForm):

    def clean_language(self):
        return self.instance.force_parent_language(
            self.parent_page) or get_default_language()


class TranslatedPage(Page):

    canonical_page = models.ForeignKey(
        'self',
        related_name='translations',
        blank=True, null=True, on_delete=models.SET_NULL,
    )

    language = models.ForeignKey(
        Language,
        on_delete=models.PROTECT,
        default=get_default_language
    )

    translation_panels = [
        MultiFieldPanel([
            FieldPanel('language'),
            PageChooserPanel('canonical_page'),
        ])
    ]

    base_form_class = AdminTranslatedPageForm

    def serve(self, request, *args, **kwargs):
        activate(self.language.code)
        return super(TranslatedPage, self).serve(request, *args, **kwargs)

    def save(self, *args, **kwargs):
        super(TranslatedPage, self).save(*args, **kwargs)
        if hasattr(self, 'force_parent_language'):
            self.force_parent_language()

    def move(self, target, pos=None):
        super(TranslatedPage, self).move(target, pos)

        if settings.WAGTAILTRANS_SYNC_TREE and self.language.is_default:
            self.move_translated_pages(canonical_target=target, pos=pos)

    def move_translated_pages(self, canonical_target, pos=None):
        """Move only the translated pages of this instance (not self)
        this is only called when WAGTAILTRANS_SYNC_TREE is enabled
        :param canonical_target: Parent of the canonical page
        :param pos: position
        """
        translations = self.get_translations(only_live=False)
        for page in translations.filter(~Q(pk=self.pk)):
            # get target because at this point we assume the tree is in sync.
            target = TranslatedPage.objects.filter(
                language=page.language, canonical_page=canonical_target).get()
            page.move(target=target, pos=pos)

    def get_translations(self, only_live=True):
        """Get translation of this page

        :param only_live: Boolean to filter on live pages
        :return: TranslatedPage instance
        """
        if self.canonical_page:
            pages = TranslatedPage.objects.filter(
                Q(canonical_page=self) |
                Q(canonical_page=self.canonical_page) |
                Q(pk=self.canonical_page.pk)
            )
        else:
            pages = TranslatedPage.objects.filter(
                Q(canonical_page=self) |
                Q(pk=self.pk)
            )

        if only_live:
            pages = pages.filter(live=True)
        pages = pages.filter(
            language__live=True
        ).order_by('language__order')
        return pages

    def create_translation(self, language, copy_fields=False):
        """Create a translation for this page. If tree syncing is enabled the
        copy will also be moved to the corresponding language tree.

        :param language: Language instance
        :param copy_fields: Boolean specifying if the content should be copied
        :param trans_root: Boolean specifying if instance is a translation root
        :return: new Translated page (or subclass) instance
        """
        if TranslatedPage.objects.filter(
                canonical_page=self,
                language=language).exists():
            raise Exception("Translation already exists")

        model_class = self.content_type.model_class()

        parent = self.get_parent()
        new_parent = parent
        if hasattr(parent, 'get_translations'):
            new_parent = parent.get_translations(only_live=False).filter(
                language=language)

        new_slug = '%s-%s' % (
            self.slug, language.code
        )
        if copy_fields:
            new_page = self.copy(
                update_attrs={
                    'slug': new_slug,
                    'language': language,
                    'live': False,
                    'canonical_page': self,
                }
            )
            if parent != new_parent:
                new_page = new_page.move(new_parent)
        else:
            new_page = model_class(
                slug=new_slug,
                title=self.title,
                language=language,
                live=False,
                canonical_page=self)

            if new_parent:
                new_page = new_parent.add_child(instance=new_page)
            else:
                new_page = self.add_sibling(instance=new_page)
        if new_page.is_first_of_language(language):
            create_group_page_permission(new_page, language)

        return new_page

    def move_translation(self, language):
        new_parent = TranslatedPage.objects.get(
            canonical_page=self.get_parent(), language=language)
        self.move(new_parent, pos='last-child')

    def force_parent_language(self, parent=None):
        """Set Page instance language to the parent language.

        :param parent: Parent page of self
        :return: Language instance
        """
        if not parent:
            parent = self.get_parent()
        if parent:
            parent = parent.content_type.get_object_for_this_type(pk=parent.pk)
            if hasattr(parent, 'language'):
                if self.language != parent.language:
                    self.language = parent.language
        return self.language

    def is_first_of_language(self, language):
        """Check if page is first of translation

        :param language: Language instance
        :return: Boolean
        """
        site = self.get_site()
        translated_pages = TranslatedPage.objects.filter(
            ~Q(pk=self.pk), language=language)
        relatives = [p for p in translated_pages if p.get_site() == site]
        return False if relatives else True


@cached_classmethod
def get_edit_handler(cls):
    tabs = []
    if cls.content_panels:
        tabs.append(ObjectList(cls.content_panels,
                               heading=ugettext_lazy('Content')))
    if cls.promote_panels:
        tabs.append(ObjectList(cls.promote_panels,
                               heading=ugettext_lazy('Promote')))
    if cls.settings_panels:
        tabs.append(ObjectList(cls.settings_panels,
                               heading=ugettext_lazy('Settings'),
                               classname='settings'))
    if cls.translation_panels:
        tabs.append(ObjectList(cls.translation_panels,
                               heading=ugettext_lazy('Translations')))

    EditHandler = TabbedInterface(tabs, base_form_class=cls.base_form_class)
    return EditHandler.bind_to_model(cls)

TranslatedPage.get_edit_handler = get_edit_handler


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
            return language.first()
    return get_default_language()


class AbstractTranslatableSiteRootPage(Page):
    """Root page of any translated site.
    This page should be used as the root page because it will route the
    requests to the right language.
    """

    def serve(self, request, *args, **kwargs):
        """Serve TranslatedPages in the correct language

        :param request: request object
        :return: Http403 or Http404
        """
        language = get_user_language(request)
        candidates = TranslatedPage.objects.live().specific().child_of(self)
        try:
            translation = candidates.filter(language=language).get()
            return redirect(translation.url)
        except TranslatedPage.DoesNotExist:
            raise Http404

    class Meta:
        abstract = True


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
