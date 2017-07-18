from .base import *  # noqa

# Load Local Settings
try:
    from .local_settings import *  # noqa
except ImportError:
    pass
