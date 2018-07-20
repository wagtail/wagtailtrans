from __future__ import absolute_import, unicode_literals

from wagtail.contrib.modeladmin.views import DeleteView


class LanguageDeleteView(DeleteView):
    """
    Custom Delete View Class for `Language` ModelAdmin.
    """
    def post(self, request, *args, **kwargs):
        """Overriding Default post method because we need to delete related
        translatable pages (if there is any) before we can delete a Language
        which are references through protected foreign key.

        TODO: Look into the posibilities to make the Language as CASCASE instead
            of PROTECTED.
        """
        if self.instance.pages.count():
            self.instance.pages.all().delete()

        return super(LanguageDeleteView, self).post(request, *args, **kwargs)
