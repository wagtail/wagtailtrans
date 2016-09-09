from django.conf import settings
from django.db.models.signals import post_save
from wagtail.wagtailcore.models import get_page_models

from wagtail.wagtailtrans.models import (
    Language, TranslatedPage, get_default_language
 )


def synchronize_trees(sender, instance, **kwargs):
    """
    synchronize the translation trees when a TranslatedPage is created or moved

    """
    if (
        not kwargs.get('created') or
        not settings.WAGTAILTRANS_SYNC_TREE or
        not getattr(instance, 'language', False) or
        not instance.language.is_default
    ):
        return

    for lang in Language.objects.filter(is_default=False):
        instance.create_translation(language=lang, copy_fields=True)


def create_new_language_tree(sender, instance, **kwargs):
    if not kwargs.get('created') or not settings.WAGTAILTRANS_SYNC_TREE:
        return
    for page in TranslatedPage.objects.filter(language=get_default_language()):
        page.create_translation(language=instance, copy_fields=True)


def register_signal_handlers():
    post_save.connect(create_new_language_tree, sender=Language)

    for model in get_page_models():
        post_save.connect(synchronize_trees, sender=model)
