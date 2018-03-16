from django import forms
from django.utils.translation import ugettext as _
from wagtail.core.models import Page

from wagtailtrans.models import TranslatablePage


class TranslationForm(forms.ModelForm):
    copy_from_canonical = forms.BooleanField(required=False)
    parent_page = forms.ModelChoiceField(queryset=TranslatablePage.objects.none())

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
        qs = TranslatablePage.objects.filter(language=self.language).exclude(id=self.instance.id)

        allowed_pages = [p.pk for p in qs.specific() if self.instance.can_move_to(p) and p.get_site() == site]

        qs = qs.filter(pk__in=allowed_pages)
        if not qs:
            return Page.objects.filter(id=site.root_page_id)
        return qs

    def _page_has_required(self, page):
        common_fields = set(TranslatablePage._meta.fields)
        specific_fields = set(page.specific._meta.fields) - common_fields
        required_fields = [f for f in specific_fields if not f.blank and not f.name.endswith('ptr')]

        return len(required_fields) > 0
