import factory
import pytest
from django.db.models import signals
from django.http import Http404
from django.test import override_settings

from wagtailtrans.models import TranslatablePage
from wagtailtrans.views import translation

from tests.factories import language, pages, sites


@pytest.mark.django_db
class TestAddTranslationView(object):

    def setup(self):
        self.default_language = language.LanguageFactory.create(code='en', is_default=True)
        self.pages = sites.create_site_tree(language=self.default_language)
        self.last_page = self.pages[-1]

    def test_get(self, rf):
        with factory.django.mute_signals(signals.post_save):  # Fake `WAGTAILTRANS_SYNC_TREE` setting
            fr = language.LanguageFactory(is_default=False, code='fr', position=2)

        assert TranslatablePage.objects.filter(language=fr).count() == 0

        view = translation.Add.as_view()
        response = view(
            rf.get('/'), page_pk=self.last_page.pk, language_code='fr')

        form = response.context_data['form']
        parent_page_qs = form.fields['parent_page'].queryset
        assert response.status_code == 200

        # The new language has been added,
        # so only the root page should be availabe as parent
        assert parent_page_qs.count() == 1
        assert parent_page_qs.model is not TranslatablePage
        assert parent_page_qs.first() == self.pages[0]

        french_root = pages.TranslatablePageFactory.build(language=fr, title="French root")
        self.pages[0].add_child(instance=french_root)

        response = view(
            rf.get('/'), page_pk=self.last_page.pk, language_code='fr')

        form = response.context_data['form']
        parent_page_qs = form.fields['parent_page'].queryset

        # We have a french page to add our new translated page to
        assert parent_page_qs.count() == 1
        assert parent_page_qs.model is TranslatablePage
        assert parent_page_qs[0].language == fr
        assert parent_page_qs[0] == french_root

    def test_post_existing(self, rf):
        """It should fail when adding an existing
        page / language combination.

        """
        request = rf.post('/', {'parent_page': self.last_page.pk})

        assert self.last_page.language.code == 'en'

        with override_settings(WAGTAILTRANS_SYNC_TREE=False):
            view = translation.Add.as_view()
            response = view(
                request, page_pk=self.last_page.pk,
                language_code=self.default_language.code)

        assert response.status_code == 200
        assert not response.context_data['form'].is_valid()

    def test_post_404(self, rf):
        """It should raise a 404 when a wrong page_pk is given."""
        view = translation.Add.as_view()
        with pytest.raises(Http404):
            view(rf.post('/'), page_pk=0, language_code='en')
