from django.test import override_settings

from wagtailtrans import conf


def test_get_wagtailtrans_setting_defaults():
    for key, value in conf.DEFAULT_SETTINGS.items():
        assert conf.get_wagtailtrans_setting(key) == value


def test_get_wagtailtrans_setting_override():
    with override_settings(WAGTAILTRANS_SYNC_TREE=False):
        assert not conf.get_wagtailtrans_setting('SYNC_TREE')
