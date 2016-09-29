from __future__ import absolute_import

import os

import django
import pytest


def pytest_configure(config):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests._sandbox.settings')
    django.setup()


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        # Remove some initial data that is brought by the sandbox module
        from wagtail.wagtailcore.models import Site, Page
        Site.objects.all().delete()
        Page.objects.all().delete()
