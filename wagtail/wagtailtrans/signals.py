from django.conf import settings
from django.db.models.signals import post_save
from wagtail.wagtailcore.models import get_page_models

from wagtail.wagtailtrans.models import Language, TranslatedPage


def synchronize_trees(sender, instance, **kwargs):
    """
    synchronize the translation trees when a TranslatedPage is created or moved

    """
    if (
        not kwargs.get('created') or
        not settings.WAGTAILTRANS_SYNC_TREE or
        not instance.language.is_default
    ):
        return

    for lang in Language.objects.filter(is_default=False):
        translation = instance.create_translation(
            language=lang, copy_fields=True)
        new_parent = TranslatedPage.objects.get(
            canonical_page=instance.get_parent(), language=lang)
        translation.move(new_parent, pos='last-child')


def register_signal_handlers():
    for model in get_page_models():
        post_save.connect(synchronize_trees, sender=model)
