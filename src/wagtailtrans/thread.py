from threading import local

_thread_locals = local()


def set_site_languages(languages):
    setattr(_thread_locals, 'site_languages', languages)


def get_site_languages():
    return getattr(_thread_locals, 'site_languages', None)
