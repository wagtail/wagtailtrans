from __future__ import absolute_import, unicode_literals

from django import forms
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic.edit import FormView

from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, ObjectList, TabbedInterface)
from wagtail.wagtailtrans.models import Language, TranslatedPage


class TranslationForm(forms.Form):
    copy_from_canonical = forms.BooleanField(required=False)


class Add(FormView):
    form_class = TranslationForm
    template_name = 'wagtailtrans/translation/add.html'

    add_panels = [
        FieldPanel('copy_from_canonical'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(add_panels, heading='Translate',
                   base_form_class=TranslationForm),
    ])

    def get(self, *args, **kwargs):
        try:
            page = TranslatedPage.objects.get(pk=kwargs['page'])
        except TranslatedPage.DoesNotExist:
            return Http404

        try:
            language = Language.objects.get(code=kwargs['language'])
        except Language.DoesNotExist:
            return Http404

        self.page = page.content_type.get_object_for_this_type(pk=page.pk)
        self.language = language
        return super(Add, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        try:
            page = TranslatedPage.objects.get(pk=kwargs['page'])
        except TranslatedPage.DoesNotExist:
            return Http404

        try:
            language = Language.objects.get(code=kwargs['language'])
        except Language.DoesNotExist:
            return Http404

        copy_from_canonical = self.request.POST.get('copy_from_canonical')
        if copy_from_canonical == u'on':
            copy_fields = True
        else:
            copy_fields = False

        page = page.content_type.get_object_for_this_type(pk=page.pk)
        new_page = page.create_translation(language, copy_fields)
        return redirect(
            'wagtailadmin_pages:edit', new_page.id)

    def get_context_data(self):
        context = super(Add, self).get_context_data()
        context['page'] = self.page
        context['language'] = self.language
        context['content_type'] = self.page.content_type
        context['parent_page'] = self.page.get_parent()
        edit_handler = self.edit_handler.bind_to_model(self.page)
        form = TranslationForm(data=dict(
            canonical_page=self.page.pk,
            language=self.language,
            copy_from_canonical=True
        ))

        context['edit_handler'] = edit_handler(self.page, form)
        return context
