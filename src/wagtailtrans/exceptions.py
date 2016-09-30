from __future__ import absolute_import, unicode_literals


class TranslationError(Exception):
    """Generic wagtailtrans error."""

    pass


class TranslationMutationError(TranslationError):
    """An error raised while performing a language change.

    This could be for example a page moving from one language to another
    or a tree structure which needs to be synced with another language tree.
    """

    pass
