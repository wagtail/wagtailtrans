from __future__ import absolute_import

import pytest
from django.test import override_settings
from wagtail.wagtailcore.models import Site, Page

from tests._sandbox.pages.models import HomePage
from wagtailtrans.models import Language, TranslatableSiteRootPage

LANG_CODES = ['es', 'fr', 'de', 'nl', 'en']


def pytest_configure(config):
    override = override_settings(
        DEBUG=False,
    )
    override.enable()


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        # Remove some initial data that is brought by the sandbox module
        Site.objects.all().delete()
        Page.objects.all().exclude(depth=1).delete()


@pytest.fixture
def sites():
    for code in LANG_CODES:
        site_root = (
            TranslatableSiteRootPage
            .add_root(title='site root %s.localhost' % code))
        site_root.save()
        language = Language.objects.get(code=code)
        page = HomePage(
            title='%s title' % code, language=language, body=u'%s body' % code)
        site_root.add_child(instance=page)
        Site.objects.create(
            hostname='%s.localhost' % code, port=8000, root_page=site_root)
    return Site.objects.all()


@pytest.fixture
def languages():
    for i, code in enumerate(LANG_CODES):
        Language.objects.get_or_create(
            code=code, defaults={
                'is_default': True,
                'position': i,
                'live': True,
            })
