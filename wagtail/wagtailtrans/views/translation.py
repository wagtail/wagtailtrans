from __future__ import absolute_import, unicode_literals

from django import forms
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.edit import FormView

from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, ObjectList, TabbedInterface, PageChooserPanel)
from wagtail.wagtailcore.models import Page

from wagtail.wagtailtrans.models import (
    Language, TranslatedPage, get_default_language)


class TranslationForm(forms.Form):
    copy_from_canonical = forms.BooleanField(required=False)
    parent_page = forms.ModelChoiceField(
        queryset=TranslatedPage.objects.filter(language__is_default=False))

    def __init__(self, *args, **kwargs):
        if kwargs.get('data'):
            super(TranslationForm, self).__init__(*args, **kwargs)
            return
        page = get_object_or_404(TranslatedPage, pk=kwargs.pop('page'))
        self.language = get_object_or_404(
            Language, code=kwargs.pop('language'))
        self.page = page.content_type.get_object_for_this_type(pk=page.pk)
        self.site = self.page.get_site()
        self.base_fields['parent_page'].queryset = self.get_queryset()
        super(TranslationForm, self).__init__(*args, **kwargs)

    def get_queryset(self):
        qs = TranslatedPage.objects.filter(language=self.language)
        allowed_pages = [p.pk for p in qs if (
            self.page.can_move_to(p) and p.get_site() == self.site
        )]
        qs = TranslatedPage.objects.filter(pk__in=allowed_pages)
        return qs if qs else self.as_language_home()

    def as_language_home(self):
        qs = TranslatedPage.objects.filter(language=get_default_language())
        keys = [p.pk for p in qs]
        roots = [p.get_parent().pk for p in qs if (
            p.get_parent().pk not in keys and p.get_site() == self.site
        )]
        return Page.objects.filter(pk__in=roots)


class Add(FormView):
    form_class = TranslationForm
    template_name = 'wagtailtrans/translation/add.html'

    add_panels = [
        FieldPanel('copy_from_canonical'),
        PageChooserPanel('parent_page'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(add_panels, heading='Translate',
                   base_form_class=TranslationForm),
    ])

    def get(self, *args, **kwargs):
        page = get_object_or_404(TranslatedPage, pk=kwargs['page'])
        self.language = get_object_or_404(Language, code=kwargs['language'])
        self.page = page.content_type.get_object_for_this_type(pk=page.pk)
        return super(Add, self).get(*args, **kwargs)

    def get_form_kwargs(self, *args, **kwargs):
        return {
            'page': self.page.pk,
            'language': self.language.code,
        }

    # FIXME: Should be checking FORM data instead of POST
    # CHECKME: Maybe the FormView works with a `def form_valid` as well
    def post(self, *args, **kwargs):
        page = get_object_or_404(TranslatedPage, pk=kwargs['page'])
        parent = get_object_or_404(
            Page, pk=self.request.POST.get('parent_page'))
        language = get_object_or_404(Language, code=kwargs['language'])
        copy_from_canonical = self.request.POST.get('copy_from_canonical')

        copy_fields = True if copy_from_canonical == u'on' else False

        page = page.content_type.get_object_for_this_type(pk=page.pk)
        new_page = page.create_translation(language, copy_fields)
        new_page.move(parent, pos='last-child')
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
