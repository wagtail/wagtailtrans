import pytest
from django.http import Http404

from django.test import RequestFactory

from wagtail.wagtailtrans.tests.factories import create_page_tree
from wagtail.wagtailtrans.views import translation
from wagtail.wagtailtrans.tests import factories


@pytest.fixture()
def rf():
    """RequestFactory instance"""
    return RequestFactory()


@pytest.mark.django_db
class TestTranslationView(object):
    def setup(self):
        self.view = translation.Add.as_view()
        self.page = create_page_tree()

    def test_get(self, rf):
        request = rf.get('/')
        response = self.view(
            request, page=self.page.pk, language=self.page.language)
        assert response.status_code == 200

    def test_post(self, rf):
        request = rf.post('/')
        response = self.view(
            request, page=self.page.pk, language=self.page.language)
        assert response.status_code == 302

    def test_post_404(self, rf):
        request = rf.post('/')
        with pytest.raises(Http404):
            self.view(request, page=self.page.pk+1, language=self.page.language)
