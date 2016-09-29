import pytest
from django.http import Http404
from django.test import override_settings

from wagtailtrans.views import translation

from tests.factories import pages, language, sites


@pytest.mark.django_db
class TestTranslationView(object):

    def setup(self):
        self.view = translation.Add.as_view()
        self.page = sites.create_site_tree()

    def test_get(self, rf):
        request = rf.get('/')
        response = self.view(
            request, page=self.page.pk, language=self.page.language)
        assert response.status_code == 200

    def test_post(self, rf):
        with override_settings(WAGTAILTRANS_SYNC_TREE=False):
            parent = pages.TranslatedPageFactory(language=self.page.language)
            lang = language.LanguageFactory(
                is_default=False, code='fr', position=2)
            request = rf.post('/', {'parent_page': parent.pk})
            response = self.view(request, page=self.page.pk, language=lang)
            assert response.status_code == 302

    def test_post_404(self, rf):
        request = rf.post('/')
        with pytest.raises(Http404):
            self.view(request, page=0, language=self.page.language)
