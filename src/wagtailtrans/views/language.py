from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy
from wagtail.wagtailadmin.views import generic
from wagtail.wagtailcore.permission_policies import ModelPermissionPolicy

from wagtailtrans.forms import LanguageForm
from wagtailtrans.models import Language

language_permission_policy = ModelPermissionPolicy(Language)


class Index(generic.IndexView):
    model = Language
    permission_policy = language_permission_policy
    context_object_name = 'languages'
    template_name = 'wagtailtrans/languages/index.html'
    add_url_name = 'wagtailtrans_languages:add'
    page_title = ugettext_lazy("Languages")
    add_item_label = ugettext_lazy("Add a language")
    header_icon = 'folder-open-1'


class Create(generic.CreateView):
    form_class = LanguageForm
    permission_policy = language_permission_policy
    page_title = ugettext_lazy("Add language")
    success_message = ugettext_lazy("Language '{0}' created.")
    add_url_name = 'wagtailtrans_languages:add'
    edit_url_name = 'wagtailtrans_languages:edit'
    index_url_name = 'wagtailtrans_languages:index'
    header_icon = 'folder-open-1'


class Edit(generic.EditView):
    model = Language
    permission_policy = language_permission_policy
    form_class = LanguageForm
    success_message = ugettext_lazy("Language '{0}' updated.")
    error_message = ugettext_lazy(
        "The language could not be saved due to errors.")
    delete_item_label = ugettext_lazy("Delete language")
    edit_url_name = 'wagtailtrans_languages:edit'
    index_url_name = 'wagtailtrans_languages:index'
    delete_url_name = 'wagtailtrans_languages:delete'
    context_object_name = 'languages'
    header_icon = 'folder-open-1'


class Delete(generic.DeleteView):
    model = Language
    permission_policy = language_permission_policy
    success_message = ugettext_lazy("Language '{0}' deleted.")
    index_url_name = 'wagtailtrans_languages:index'
    delete_url_name = 'wagtailtrans_languages:delete'
    page_title = ugettext_lazy("Delete language")
    confirmation_message = ugettext_lazy(
        "Are you sure you want to delete this language?")
    header_icon = 'folder-open-1'
