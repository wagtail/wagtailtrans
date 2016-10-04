import pytest
from django.http import Http404
from django.test import override_settings

from tests.factories import language, sites, pages
from wagtailtrans.models import Language, TranslatablePage
from wagtailtrans.views import translation


@pytest.mark.django_db
class TestAddTranslationView(object):

    def setup(self):
        self.view = translation.Add.as_view()
        self.default_language = Language.objects.get(code='en')

        self.pages = sites.create_site_tree(language=self.default_language)
        self.last_page = self.pages[-1]

        with override_settings(WAGTAILTRANS_SYNC_TREE=False):
            self.new_lang = language.LanguageFactory(is_default=False,
                                                     code='fr', position=2)

    def test_get(self, rf):
        request = rf.get('/')
        response = self.view(request,
                             page_pk=self.last_page.pk,
                             language_code=self.new_lang.code)
        parent_page_qs = response.context_data['form'].fields[
            'parent_page'].queryset
        assert response.status_code == 200

        # The new language has been added,
        # so only the root page should be availabe as parent
        assert parent_page_qs.count() == 1
        assert parent_page_qs.model is not TranslatablePage

        french_root = pages.TranslatablePageFactory.build(
            language=self.new_lang, title="French root")
        self.pages[0].add_child(instance=french_root)

        response = self.view(request,
                             page_pk=self.last_page.pk,
                             language_code=self.new_lang.code)
        parent_page_qs = response.context_data['form'].fields[
            'parent_page'].queryset
        # We have a french page to add our new translated page to
        assert parent_page_qs.count() == 1
        assert parent_page_qs.model is TranslatablePage
        assert parent_page_qs[0].language == self.new_lang
        assert parent_page_qs[0] == french_root

    def test_post_existing(self, rf):
        """It should fail when adding an existing page / language combination.

        """
        with override_settings(WAGTAILTRANS_SYNC_TREE=False):
            request = rf.post('/', {'parent_page': self.last_page.pk})
            response = self.view(
                request, page_pk=self.last_page.pk,
                language_code=self.default_language.code)

            assert response.status_code == 200
            assert not response.context_data['form'].is_valid()

    def test_post_404(self, rf):
        """It should raise a 404 when a wrong page_pk is given."""
        request = rf.post('/')
        with pytest.raises(Http404):
            self.view(request, page_pk=0,
                      language_code=self.last_page.language)
