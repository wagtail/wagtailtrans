from django.db.models.signals import post_save
from django.dispatch import receiver

from wagtail.wagtailtrans.models import TranslatedPage


@receiver(post_save, sender=TranslatedPage)
def sync_translation_trees(sender, instance, **kwargs):
    """
    Trees should be synced when a new page is created in the canonical tree
    """
