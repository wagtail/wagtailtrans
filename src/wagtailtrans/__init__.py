default_app_config = 'wagtailtrans.apps.WagtailTransConfig'

VERSION = (2, 0, 0, 'final')


def get_version():
    """Return normalised version string."""
    version = '%s.%s' % (VERSION[0], VERSION[1])
    # Append 3rd digit if > 0
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])

    if VERSION[3] != 'final':
        version = '%s.%s' % (version, VERSION[3])
    return version
