import pytest
from django.http import Http404

from django.test import RequestFactory, override_settings

from wagtail.wagtailtrans.tests.factories import create_site_tree
from wagtail.wagtailtrans.views import translation
from wagtail.wagtailtrans.tests import factories


@pytest.mark.django_db
class TestTranslationView(object):
    def setup(self):
        self.view = translation.Add.as_view()
        self.page = create_site_tree()
        self.rf = RequestFactory()

    def test_get(self):
        request = self.rf.get('/')
        response = self.view(
            request, page=self.page.pk, language=self.page.language)
        assert response.status_code == 200

    @override_settings(WAGTAILTRANS_SYNC_TREE=False)
    def test_post(self):
        parent = factories.TranslatedPageFactory(language=self.page.language)
        lang = factories.LanguageFactory(is_default=False, code='fr', order=2)
        request = self.rf.post('/', {'parent_page': parent.pk})
        response = self.view(request, page=self.page.pk, language=lang)
        assert response.status_code == 302

    def test_post_404(self):
        request = self.rf.post('/')
        with pytest.raises(Http404):
            self.view(
                request, page=self.page.pk + 1, language=self.page.language)
