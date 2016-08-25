from __future__ import absolute_import, unicode_literals

from django.http import Http404
from django import forms
from django.views.generic.edit import FormView
from wagtail.wagtailcore.models import Page


class TranslationForm(forms.Form):
    canonical_page = forms.IntegerField()
    copy_from_canonical = forms.BooleanField()
    language = forms.CharField()


class Add(FormView):
    form_class = TranslationForm
    template_name = 'wagtailtrans/translation/add.html'
    success_url = '/'

    def get(self, *args, **kwargs):
        try:
            page = Page.objects.get(pk=kwargs['page'])
        except Page.DoesNotExist:
            return Http404

        self.page = page.content_type.get_object_for_this_type(pk=page.pk)
        return super(Add, self).get(*args, **kwargs)

    def get_context_data(self):
        context = super(Add, self).get_context_data()
        return context
