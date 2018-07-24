import factory
import pytest
from django.contrib.auth.models import Permission
from django.contrib.messages.storage.fallback import FallbackStorage
from django.db.models import signals
from django.http import Http404
from django.test import override_settings

from tests.factories import language, pages, sites, users
from wagtailtrans.models import Language, TranslatablePage
from wagtailtrans.views.language import LanguageDeleteView
from wagtailtrans.views.translation import TranslationView
from wagtailtrans.wagtail_hooks import LanguageModelAdmin


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

        view = TranslationView()
        view.request = request
        response = view.dispatch(request, instance_id=self.last_page.pk, language_code='fr')

        parent_page_qs = view.get_form().fields['parent_page'].queryset

        assert response.status_code == 200
        assert parent_page_qs.count() == 1
        assert parent_page_qs.model is not TranslatablePage
        assert parent_page_qs.first() == self.pages[0]

        french_root = pages.TranslatablePageFactory.build(language=fr, title="French root")
        self.pages[0].add_child(instance=french_root)

        response = view.dispatch(request, instance_id=self.last_page.pk, language_code='fr')

        parent_page_qs = view.get_form().fields['parent_page'].queryset

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

        view = TranslationView()
        view.request = request
        response = view.dispatch(request, instance_id=self.pages[1].pk, language_code='de')

        assert response.status_code == 302
        assert response['Location'].endswith('/edit/')

    def test_post_existing(self, rf):
        """It should fail when adding an existing
        page / language combination.

        """
        request = rf.post('/', {'parent_page': self.last_page.pk})

        assert self.last_page.language.code == 'en'

        with override_settings(WAGTAILTRANS_SYNC_TREE=False):
            view = TranslationView()
            view.request = request
            response = view.dispatch(request, instance_id=self.last_page.pk, language_code=self.default_language.code)

        assert response.status_code == 200
        assert not view.get_form().is_valid()

    def test_post_404(self, rf):
        """It should raise a 404 when a wrong page_pk is given."""
        view = TranslationView.as_view()
        with pytest.raises(Http404):
            view(rf.post('/'), instance_id=0, language_code='en')


@pytest.mark.django_db
class TestLanguageAdminView(object):

    def setup(self):
        self.language = language.LanguageFactory()

    def test_response_language_add_view(self, admin_client):
        response = admin_client.get('/admin/wagtailtrans/language/create/')
        assert response.status_code == 200

    def test_response_language_edit_view(self, admin_client):
        response = admin_client.get('/admin/wagtailtrans/language/edit/%d/' % self.language.pk)
        assert response.status_code == 200


@pytest.mark.django_db
class TestLanguageDeleteView(object):

    def setup(self):
        self.default_language = language.LanguageFactory.create(code='en', is_default=True)
        self.pages = sites.create_site_tree(language=self.default_language)
        self.second_language = language.LanguageFactory(is_default=False, code='fr', position=2)
        self.view = lambda language: LanguageDeleteView(
            instance_pk=str(language.pk),
            model_admin=LanguageModelAdmin()
        )

    def test_post(self, rf):
        """
        When we delete non canonical language it should also delete the related
        pages.

        After a successfull post request the language and related pages for
        that specific language should be deleted.
        """
        request = rf.post('/')

        user = users.UserFactory()
        admin_perm = Permission.objects.get(
            content_type__app_label='wagtailadmin', codename='access_admin')
        del_wagtailtrans_lang_perm = Permission.objects.get(
            content_type__app_label='wagtailtrans', codename='delete_language')
        user.user_permissions.add(admin_perm, del_wagtailtrans_lang_perm)
        request.user = user

        # Add messages to request
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        # Language and Pages exists before post request
        assert TranslatablePage.objects.count() == 6
        assert TranslatablePage.objects.filter(language=self.second_language).count() == 3
        assert self.second_language in Language.objects.all()

        response = self.view(self.second_language).dispatch(request)

        # Second Language and Pages should not exists after post request.
        assert TranslatablePage.objects.count() == 3
        assert TranslatablePage.objects.filter(language=self.second_language).count() == 0
        assert self.second_language not in Language.objects.all()

        # New messages should be added
        assert messages.added_new

        # after a successfull post request it should redirect to index page.
        assert response.status_code == 302
        assert response['Location'].endswith('/language/')


    def test_post_default(self, rf):
        """
        We should't delete the default language.
        """
        request = rf.post('/')

        user = users.UserFactory()
        admin_perm = Permission.objects.get(
            content_type__app_label='wagtailadmin', codename='access_admin')
        del_wagtailtrans_lang_perm = Permission.objects.get(
            content_type__app_label='wagtailtrans', codename='delete_language')
        user.user_permissions.add(admin_perm, del_wagtailtrans_lang_perm)
        request.user = user

        # Add messages to request
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        # Default Language and Pages exists before post request
        assert TranslatablePage.objects.count() == 6
        assert TranslatablePage.objects.filter(language=self.default_language).count() == 3
        assert self.default_language in Language.objects.all()

        with pytest.raises(Exception) as excinfo:
            response = self.view(self.default_language).dispatch(request)

        # should raise proper error
        assert repr(excinfo.value) == 'Exception("Can\'t delete a default language",)'
