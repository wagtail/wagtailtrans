from __future__ import absolute_import, unicode_literals

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from wagtail.wagtailadmin.views.generic import CreateView

from wagtailtrans.forms import TranslationForm
from wagtailtrans.models import Language, TranslatablePage


class TranslationView(CreateView):
    model = TranslatablePage
    form_class = TranslationForm

    def page_title(self):
        return _("Translate {} to {}".format(
            self.instance.get_admin_display_title(), self.language))

    def get_add_url(self):
        return reverse(
            'wagtailtrans_translations:add',
            args=(self.instance.id, self.language.code))

    def dispatch(self, request, instance_id, language_code, *args, **kwargs):
        self.language = get_object_or_404(Language, code=language_code)
        self.instance = get_object_or_404(
            TranslatablePage, id=instance_id).specific
        return super(TranslationView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        self.form = self.form_class(
            instance=self.instance, language=self.language)
        return self.render_to_response()

    def post(self, request):
        self.form = self.form_class(
            request.POST, instance=self.instance, language=self.language)
        if self.form.is_valid():
            parent = self.form.cleaned_data['parent_page']
            copy_from_canonical = self.form.cleaned_data['copy_from_canonical']
            new_page = self.instance.create_translation(
                self.language, copy_fields=copy_from_canonical, parent=parent)
            return redirect('wagtailadmin_pages:edit', new_page.id)
        else:
            return self.render_to_response()
