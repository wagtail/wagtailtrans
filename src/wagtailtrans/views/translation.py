from __future__ import absolute_import, unicode_literals

from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import FormView
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, ObjectList, PageChooserPanel, TabbedInterface)

from wagtailtrans.forms import TranslationForm
from wagtailtrans.models import Language, TranslatablePage


class Add(FormView):
    """View to add a new ``Translation``."""

    form_class = TranslationForm
    template_name = 'wagtailtrans/translation/add.html'

    edit_handler = TabbedInterface([
        ObjectList(
            [
                FieldPanel('copy_from_canonical'),
                PageChooserPanel('parent_page'),
            ],
            heading=_("Translate"),
            base_form_class=TranslationForm
        ),
    ])

    def dispatch(self, request, page_pk, language_code, *args, **kwargs):
        self.page = get_object_or_404(TranslatablePage, pk=page_pk).specific
        self.language = get_object_or_404(Language, code=language_code)
        return super(Add, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super(Add, self).get_form_kwargs(*args, **kwargs)
        form_kwargs.update({
            'page': self.page,
            'language': self.language,
        })
        return form_kwargs

    def form_valid(self, form):
        parent = form.cleaned_data['parent_page']
        copy_from_canonical = form.cleaned_data['copy_from_canonical']

        new_page = self.page.create_translation(
            self.language, copy_fields=copy_from_canonical, parent=parent)
        return redirect('wagtailadmin_pages:edit', new_page.id)

    def get_context_data(self, *args, **kwargs):
        context = super(Add, self).get_context_data(*args, **kwargs)
        edit_handler = self.edit_handler.bind_to_model(self.page)

        context.update({
            'page': self.page,
            'language': self.language,
            'content_type': self.page.content_type,
            'parent_page': self.page.get_parent(),
            'edit_handler': edit_handler(self.page, context['form']),
        })

        return context
