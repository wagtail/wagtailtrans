from os import path

default_app_config = 'wagtailtrans.config.WagtailTransConfig'

VERSION = (0, 1, 1, 'final')

WAGTAILTRANS_TEMPLATE_DIR = path.join(path.dirname(__file__), 'templates')


def get_version():
    """Return normalised version string."""
    version = '%s.%s' % (VERSION[0], VERSION[1])
    # Append 3rd digit if > 0
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    elif VERSION[3] != 'final':
        version = '%s %s' % (version, VERSION[3])
        if len(VERSION) == 5:
            version = '%s %s' % (version, VERSION[4])
    return version
