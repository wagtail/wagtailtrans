from __future__ import absolute_import

import os

import django
from django.conf import settings, global_settings

from tests._sandbox.settings import base


def pytest_configure(config):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests._sandbox.settings')

    django.setup()
