from __future__ import absolute_import, unicode_literals

from django import forms

from wagtailtrans.models import Language, TranslatedPage


class LanguageForm(forms.ModelForm):
    class Meta:
        model = Language
        fields = (
            'code',
            'is_default',
            'order',
            'live',
        )


class TranslationForm(forms.Form):
    copy_from_canonical = forms.BooleanField(required=False)
    parent_page = forms.ModelChoiceField(
        queryset=TranslatedPage.objects.filter(language__is_default=False))

    def __init__(self, *args, **kwargs):
        self.page = kwargs.pop('page')
        self.site = self.page.get_site()
        self.language = kwargs.pop('language')
        self.base_fields['parent_page'].queryset = self.get_queryset()
        super(TranslationForm, self).__init__(*args, **kwargs)

    def get_queryset(self):
        qs = TranslatedPage.objects.filter(language=self.language)
        allowed_pages = [p.pk for p in qs if (
            self.page.can_move_to(p) and p.get_site() == self.site
        )]
        return TranslatedPage.objects.filter(pk__in=allowed_pages)
