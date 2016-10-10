from __future__ import absolute_import, unicode_literals

from operator import itemgetter

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _
from wagtail.wagtailcore.models import Page

from wagtailtrans.models import Language, TranslatablePage


class LanguageForm(forms.ModelForm):

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

        # Disable `is_default` field when a default language is already set.
        if Language.objects.default() and settings.WAGTAILTRANS_SYNC_TREE:
            self.fields['is_default'].widget.attrs['disabled'] = 'disabled'
            self.fields['is_default'].help_text = _("""
                There can only be one default language, this
                can't be changed when in SYNC mode.""")

    def clean_is_default(self):
        """Force the `is_default` to stay the same, when in sync mode."""
        if (
            self.instance and
            settings.WAGTAILTRANS_SYNC_TREE and
            Language.objects.default()
        ):
            return self.instance.is_default
        return self.cleaned_data['is_default']


class TranslationForm(forms.Form):
    copy_from_canonical = forms.BooleanField(required=False)
    parent_page = forms.ModelChoiceField(
        queryset=TranslatablePage.objects.filter(language__is_default=False))

    def __init__(self, *args, **kwargs):
        self.page = kwargs.pop('page')
        self.site = self.page.get_site()
        self.language = kwargs.pop('language')
        self.base_fields['parent_page'].queryset = self.get_queryset()

        if self._page_has_required(self.page):
            self.base_fields['copy_from_canonical'].initial = True
            self.base_fields['copy_from_canonical'].disabled = True
            self.base_fields['copy_from_canonical'].help_text = _(
                "All fields need to be copied because of some required fields")

        super(TranslationForm, self).__init__(*args, **kwargs)

    def get_queryset(self):
        qs = TranslatablePage.objects.filter(language=self.language)
        allowed_pages = [p.pk for p in qs if (
            self.page.can_move_to(p) and p.get_site() == self.site
        )]
        qs = TranslatablePage.objects.filter(pk__in=allowed_pages)
        if not qs:
            return Page.objects.filter(pk=self.site.root_page.pk)
        return qs

    def _page_has_required(self, page):
        common_fields = set(TranslatablePage._meta.fields)
        specific_fields = set(page.specific._meta.fields) - common_fields

        required_fields = [f for f in specific_fields
                           if not f.blank and not f.name.endswith('ptr')]
        if required_fields:
            return True
        return False
