from operator import itemgetter

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect
from django.utils.encoding import force_text
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import activate
from wagtail.contrib.settings.models import BaseSetting
from wagtail.contrib.settings.registry import register_setting
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, PageChooserPanel
from wagtail.admin.forms import WagtailAdminModelForm, WagtailAdminPageForm
from wagtail.core.models import Page
from wagtail.search.index import FilterField

from .conf import get_wagtailtrans_setting
from .edit_handlers import CanonicalPageWidget, ReadOnlyWidget
from .managers import LanguageManager
from .permissions import TranslatableUserPagePermissionsProxy


class WagtailAdminLanguageForm(WagtailAdminModelForm):
    """Custom wagtailadmin form so we can make use of the panels
    property, used by ``wagtail.contrib.modeladmin``.

    """
    code = forms.ChoiceField(
        label=_("Language"), choices=settings.LANGUAGES,
        help_text=_("One of the languages defined in LANGUAGES"))

    class Meta:
        fields = [
            'code',
            'is_default',
            'position',
            'live',
        ]

    def __init__(self, *args, **kwargs):
        super(WagtailAdminLanguageForm, self).__init__(*args, **kwargs)

        sorted_choices = sorted(self.fields['code'].choices, key=itemgetter(1))
        self.fields['code'].choices = sorted_choices

    def clean_is_default(self):
        is_default = self.cleaned_data['is_default']

        if self.initial.get('is_default') and not is_default:
            raise ValidationError(_(
                "You can not remove is_default from a language. To change the "
                "default language, select is_default on a different language"))

        return is_default

    def save(self, commit=True):
        is_default = self.cleaned_data.get('is_default', False)
        if (
            not self.initial.get('is_default') == is_default and
            is_default and
            not get_wagtailtrans_setting('LANGUAGES_PER_SITE')
        ):
            from wagtailtrans.utils.language_switch import change_default_language  # noqa
            change_default_language(self.instance)
        return super(WagtailAdminLanguageForm, self).save(commit=commit)


def get_language_panels():
    children = [
        FieldPanel('code'),
        FieldPanel('position'),
        FieldPanel('live'),
    ]

    if not get_wagtailtrans_setting('LANGUAGES_PER_SITE'):
        children.insert(1, FieldPanel('is_default'))

    return [
        MultiFieldPanel(heading=_("Language details"), children=children),
    ]


class Language(models.Model):
    """User defined language."""
    code = models.CharField(max_length=12, unique=True)

    is_default = models.BooleanField(
        default=False, help_text="""Visitors with no language preference will see the site in this language""")

    position = models.IntegerField(
        default=0, help_text="""Language choices and translations will be displayed in this order""")

    live = models.BooleanField(default=True, help_text="Is this language available for visitors to view?")

    objects = LanguageManager()

    base_form_class = WagtailAdminLanguageForm
    panels = get_language_panels()

    class Meta:
        ordering = ['position']

    def __str__(self):
        return force_text(dict(settings.LANGUAGES).get(self.code))

    def has_pages_in_site(self, site):
        return self.pages.filter(path__startswith=site.root_page.path).exists()


class AdminTranslatablePageForm(WagtailAdminPageForm):
    """Form to be used in the wagtail admin."""

    def __init__(self, *args, **kwargs):
        super(AdminTranslatablePageForm, self).__init__(*args, **kwargs)

        self.fields['canonical_page'].widget = CanonicalPageWidget(
            canonical_page=self.instance.specific.canonical_page)

        language_display = Language.objects.filter(pk=self.initial['language']).first()
        if self.instance.specific.is_canonical and language_display:
            language_display = "{} - {}".format(language_display, "canonical")

        self.fields['language'].widget = ReadOnlyWidget(text_display=language_display if language_display else '')


def _language_default():
    # Let the default return a PK, so migrations can also work with this value.
    # The FakeORM model in the migrations differ from this Django model.
    default_language = Language.objects.default()
    if default_language is None:
        return None
    else:
        return default_language.pk


class TranslatablePage(Page):

    #: Defined with a unique name, to prevent field clashes..
    translatable_page_ptr = models.OneToOneField(Page, parent_link=True, related_name='+', on_delete=models.CASCADE)
    canonical_page = models.ForeignKey(
        'self', related_name='translations', blank=True, null=True, on_delete=models.SET_NULL)
    language = models.ForeignKey(Language, related_name='pages', on_delete=models.PROTECT, default=_language_default)

    is_creatable = False

    search_fields = Page.search_fields + [
        FilterField('language_id'),
    ]

    settings_panels = Page.settings_panels + [
        MultiFieldPanel(
            heading=_("Translations"),
            children=[
                FieldPanel('language'),
                PageChooserPanel('canonical_page'),
            ]
        )
    ]

    base_form_class = AdminTranslatablePageForm

    def get_admin_display_title(self):
        return "{} ({})".format(super(TranslatablePage, self).get_admin_display_title(), self.language)

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

        if get_wagtailtrans_setting('LANGUAGES_PER_SITE'):
            site = self.get_site()
            lang_settings = SiteLanguages.for_site(site)
            is_default = lang_settings.default_language == self.language
        else:
            is_default = self.language.is_default

        if not suppress_sync and get_wagtailtrans_setting('SYNC_TREE') and is_default:
            self.move_translated_pages(canonical_target=target, pos=pos)

    def move_translated_pages(self, canonical_target, pos=None):
        """Move only the translated pages of this instance (not self).

        This is only called when WAGTAILTRANS_SYNC_TREE is enabled

        :param canonical_target: Parent of the canonical page
        :param pos: position

        """
        translations = self.get_translations(only_live=False)
        if getattr(canonical_target, 'canonical_page', False):
            canonical_target = canonical_target.canonical_page

        for page in translations:
            # get target because at this point we assume the tree is in sync.
            target = TranslatablePage.objects.filter(
                Q(language=page.language),
                Q(canonical_page=canonical_target) | Q(pk=canonical_target.pk)
            ).get()

            page.move(target=target, pos=pos, suppress_sync=True)

    def get_translations(self, only_live=True, include_self=False):
        """Get all translations of this page.

        This page itself is not included in the result, all pages
        are sorted by the language position.

        :param only_live: Boolean to filter on live pages & languages.
        :return: TranslatablePage instance

        """
        canonical_page_id = self.canonical_page_id or self.pk
        translations = TranslatablePage.objects.filter(Q(canonical_page=canonical_page_id) | Q(pk=canonical_page_id))

        if not include_self:
            translations = translations.exclude(pk=self.pk)

        if only_live:
            translations = translations.live().filter(language__live=True)

        return translations

    def has_translation(self, language):
        """Check if page isn't already translated in given language.

        :param language: Language instance
        :return: Boolean

        """
        return language.pages.filter(canonical_page=self).exists()

    def get_translation_parent(self, language):
        site = self.get_site()
        if not language.has_pages_in_site(site):
            return site.root_page

        translation_parent = (
            TranslatablePage.objects
            .filter(canonical_page=self.get_parent(), language=language, path__startswith=site.root_page.path)
            .first()
        )
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

        if self.slug == self.language.code:
            slug = language.code
        else:
            slug = '%s-%s' % (self.slug, language.code)

        update_attrs = {
            'title': self.title,
            'slug': slug,
            'language': language,
            'live': False,
            'canonical_page': self,
        }

        if copy_fields:
            kwargs = {'update_attrs': update_attrs}
            if parent != self.get_parent():
                kwargs['to'] = parent

            new_page = self.copy(**kwargs)
        else:
            model_class = self.content_type.model_class()
            new_page = model_class(**update_attrs)
            parent.add_child(instance=new_page)

        return new_page

    @cached_property
    def has_translations(self):
        return self.translations.exists()

    @cached_property
    def is_canonical(self):
        return not self.canonical_page_id and self.has_translations


def get_user_language(request):
    """Get the Language corresponding to a request.
    return default language if Language does not exist in site

    :param request: Request object
    :return: Language instance
    """
    if hasattr(request, 'LANGUAGE_CODE'):
        language = Language.objects.live().filter(code=request.LANGUAGE_CODE).first()
        if language:
            return language
    return Language.objects.default_for_site(site=request.site)


class TranslatableSiteRootPage(Page):
    """Root page of any translatable site.

    This page should be used as the root page because it will
    route the requests to the right language.

    """
    parent_page_types = ['wagtailcore.Page']

    def serve(self, request, *args, **kwargs):
        """Serve TranslatablePage in the correct language

        :param request: request object
        :return: Http302 or Http404

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


class SiteLanguagesForm(WagtailAdminModelForm):
    """Form to be used in the wagtail admin."""

    def save(self, commit=True):
        data = self.cleaned_data
        if not data['default_language'].pk == self.initial['default_language']:
            from wagtailtrans.utils.language_switch import change_default_language  # noqa
            change_default_language(data['default_language'], self.instance.site)

        return super(SiteLanguagesForm, self).save(commit=commit)


def register_site_languages():
    def decorate(func):
        if get_wagtailtrans_setting('LANGUAGES_PER_SITE'):
            return register_setting(func)
        return func
    return decorate


@register_site_languages()
class SiteLanguages(BaseSetting):
    """Site specific settings are stored in the database"""
    default_language = models.ForeignKey(
        Language, related_name="site_default_language", null=True, on_delete=models.PROTECT)
    other_languages = models.ManyToManyField(Language, blank=True)

    panels = [
        MultiFieldPanel(
            heading=_("Languages"),
            children=[
                FieldPanel('default_language'),
                FieldPanel(
                    'other_languages', widget=forms.CheckboxSelectMultiple),
            ]
        ),
    ]

    base_form_class = SiteLanguagesForm

    class Meta:
        verbose_name = _("Site languages")
        verbose_name_plural = _("Site languages")
