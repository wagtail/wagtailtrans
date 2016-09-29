import pytest
from django.http import HttpRequest

from wagtail.wagtailcore.models import Site
from wagtailtrans.models import Language
from tests._sandbox.pages.models import HomePage, TranslatableSiteRootPage

LANG_CODES = ['es', 'fr', 'de', 'nl']


@pytest.fixture
def languages():
    order = 1
    for code in LANG_CODES:
        Language.objects.create(
            code=code,
            order=order
        )
        order += 1
    return Language.objects.all()


@pytest.fixture
def sites():
    for code in LANG_CODES:
        site_root = TranslatableSiteRootPage.add_root(
            title='site root %s.localhost' % code,
        )
        site_root.save()
        language = Language.objects.get(code=code)
        page = HomePage(
            title='%s title' % code,
            language=language,
            body=u'%s body' % code,
        )
        site_root.add_child(instance=page)
        Site.objects.create(
            hostname='%s.localhost' % code,
            port=8000,
            root_page=site_root)
    return Site.objects.all()


@pytest.mark.django_db
class TestTranslatableSiteRootPage(object):
    def test_create(self):
        site_root = TranslatableSiteRootPage(
            title='site root'
        )
        assert site_root


@pytest.mark.django_db
class TestHomePage(object):
    def test_create(self, languages, sites):
        site = sites.get(hostname='es.localhost')
        request = HttpRequest()
        request.path = '/'
        request.META['HTTP_HOST'] = 'es.localhost'
        request.META['SERVER_PORT'] = 8000

        assert Site.find_for_request(request) == site
