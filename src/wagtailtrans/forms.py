from __future__ import absolute_import, unicode_literals

from operator import itemgetter

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _
from wagtail.wagtailcore.models import Page

from wagtailtrans.models import Language, TranslatablePage
from wagtailtrans.utils.conf import get_wagtailtrans_setting


class LanguageForm(forms.ModelForm):
    """Custom language form.

    Using a custom form which sets the choices for the `code`
    field prevents us to have new migrations when settings change.
    """
    code = forms.ChoiceField(
        label=_("Language"), choices=settings.LANGUAGES,
        help_text=_("One of the languages defined in LANGUAGES"))

    class Meta:
        model = Language
        fields = (
            'code',
            'is_default',
            'position',
            'live',
        )

    def __init__(self, *args, **kwargs):
        super(LanguageForm, self).__init__(*args, **kwargs)

        # Sort language choices according their display name
        sorted_choices = sorted(self.fields['code'].choices, key=itemgetter(1))
        self.fields['code'].choices = sorted_choices

        # Remove is_default when a default is set.
        default_language = Language.objects.default()
        if default_language and (
                get_wagtailtrans_setting('LANGUAGES_PER_SITE') or
                get_wagtailtrans_setting('SYNC_TREE')):
            del self.fields['is_default']

    def clean_is_default(self):
        """Force the `is_default` to stay the same, when in sync mode."""
        if (
            self.instance and
            get_wagtailtrans_setting('SYNC_TREE') and
            Language.objects.default()
        ):
            return self.instance.is_default
        return self.cleaned_data['is_default']


class TranslationForm(forms.ModelForm):
    copy_from_canonical = forms.BooleanField(required=False)
    parent_page = forms.ModelChoiceField(
        queryset=TranslatablePage.objects.none())

    class Meta:
        model = TranslatablePage
        fields = ['copy_from_canonical', 'parent_page']

    def __init__(self, *args, **kwargs):
        self.language = kwargs.pop('language')
        super(TranslationForm, self).__init__(*args, **kwargs)
        self.fields['parent_page'].queryset = self.get_queryset()

        if self._page_has_required(kwargs.get('instance')):
            self.fields['copy_from_canonical'].initial = True
            self.fields['copy_from_canonical'].disabled = True
            self.fields['copy_from_canonical'].help_text = _(
                "All fields need to be copied because of some required fields")

    def get_queryset(self):
        site = self.instance.get_site()
        qs = (
            TranslatablePage.objects
            .filter(language=self.language)
            .exclude(id=self.instance.id))

        allowed_pages = [
            p.pk for p in qs.specific()
            if self.instance.can_move_to(p) and p.get_site() == site
        ]

        qs = qs.filter(pk__in=allowed_pages)
        if not qs:
            return Page.objects.filter(id=site.root_page_id)
        return qs

    def _page_has_required(self, page):
        common_fields = set(TranslatablePage._meta.fields)
        specific_fields = set(page.specific._meta.fields) - common_fields
        required_fields = [
            f for f in specific_fields
            if not f.blank and not f.name.endswith('ptr')
        ]

        return len(required_fields) > 0
