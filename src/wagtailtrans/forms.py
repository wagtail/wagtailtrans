from operator import itemgetter

from django import forms

from wagtailtrans.models import Language


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

