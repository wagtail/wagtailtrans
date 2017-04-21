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

        request = rf.get('/')

        view = translation.TranslationView()
        view.request = request
        response = view.dispatch(
            request, instance_id=self.last_page.pk, language_code='fr')

        parent_page_qs = view.form['parent_page'].field.queryset

        assert response.status_code == 200
        assert parent_page_qs.count() == 1
        assert parent_page_qs.model is not TranslatablePage
        assert parent_page_qs.first() == self.pages[0]

        french_root = pages.TranslatablePageFactory.build(language=fr, title="French root")
        self.pages[0].add_child(instance=french_root)

        response = view.dispatch(
            request, instance_id=self.last_page.pk, language_code='fr')

        parent_page_qs = view.form['parent_page'].field.queryset
        # We have a french page to add our new translated page to
        assert parent_page_qs.count() == 1
        assert parent_page_qs.model is TranslatablePage
        assert parent_page_qs[0].language == fr
        assert parent_page_qs[0] == french_root

    def test_post(self, rf):
        with factory.django.mute_signals(signals.post_save):  # Fake SYNC_TREE=False
            de = language.LanguageFactory(is_default=False, code='de', position=3)

        assert TranslatablePage.objects.filter(language=de).count() == 0

        request = rf.post('/', {'parent_page': self.pages[0].pk, 'copy_from_canonical': True})

        view = translation.TranslationView()
        view.request = request
        response = view.dispatch(
            request, instance_id=self.pages[1].pk, language_code='de')

        assert response.status_code == 302
        assert response['Location'].endswith('/edit/')

    def test_post_existing(self, rf):
        """It should fail when adding an existing
        page / language combination.

        """
        request = rf.post('/', {'parent_page': self.last_page.pk})

        assert self.last_page.language.code == 'en'

        with override_settings(WAGTAILTRANS_SYNC_TREE=False):
            view = translation.TranslationView()
            view.request = request
            response = view.dispatch(
                request, instance_id=self.last_page.pk,
                language_code=self.default_language.code)

        assert response.status_code == 200
        assert not view.form.is_valid()

    def test_post_404(self, rf):
        """It should raise a 404 when a wrong page_pk is given."""
        view = translation.TranslationView.as_view()
        with pytest.raises(Http404):
            view(rf.post('/'), instance_id=0, language_code='en')
