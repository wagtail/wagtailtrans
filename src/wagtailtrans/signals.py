from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.db.models.signals import post_save, pre_delete
from wagtail.wagtailcore.models import get_page_models, Site

from wagtailtrans.models import (
    Language, TranslatedPage, get_default_language)
from wagtailtrans.permissions import get_or_create_language_group


def synchronize_trees(sender, instance, **kwargs):
    """synchronize the translation trees when
    a TranslatedPage is created or moved
    :param sender: Sender model
    :param instance: TranslatedPage instance
    :param kwargs: kwargs e.g. created
    """
    if (
        not kwargs.get('created') or
        not settings.WAGTAILTRANS_SYNC_TREE or
        not getattr(instance, 'language', False) or
        not instance.language.is_default
    ):
        return
    try:
        site = instance.get_site()
    except ObjectDoesNotExist:
        return

    relatives = TranslatedPage.objects.filter(
        ~Q(pk=instance.pk), language=get_default_language())
    relatives = [p for p in relatives if p.get_site() == site]
    for lang in Language.objects.filter(is_default=False):
        new_page = instance.create_translation(language=lang, copy_fields=True)
        new_page.language = lang
        if relatives:
            new_page.move_translation(lang)


def synchronize_deletions(sender, instance, **kwargs):
    """We use pre_delete because when sync is disabled the foreign_key on
    canonical pages on_delete is set_null.

    :param sender: Sender model
    :param instance: TranslatedPage Instance
    :param kwargs: kwargs
    """
    page = TranslatedPage.objects.filter(pk=instance.pk).first()
    if settings.WAGTAILTRANS_SYNC_TREE and page:
        TranslatedPage.objects.filter(canonical_page=page).delete()


def create_new_language_tree(sender, instance, **kwargs):
    """Signal will catch creation of a new language
    If sync trees is enabled it will create a whole new tree with
    correlating language.

    :param sender: Sender model
    :param instance: Language instance
    :param kwargs: kwargs e.g. created
    """
    get_or_create_language_group(instance)
    if not kwargs.get('created') or not settings.WAGTAILTRANS_SYNC_TREE:
        return
    for site in Site.objects.all():
        root = TranslatedPage.objects.filter(
            pk__in=site.root_page.get_children().values_list('pk', flat=True),
            language=get_default_language()).first()
        if root:
            root.create_translation(
                language=instance, copy_fields=True)
            for child_page in root.get_descendants():
                new_page = child_page.specific.create_translation(
                    language=instance, copy_fields=True)
                new_page.language = instance
                new_page.move_translation(instance)


def register_signal_handlers():
    """Registers signal handlers.
    To create a signal for TranslatedPages we have to use wagtails
    get_page_model.
    """
    post_save.connect(create_new_language_tree, sender=Language)

    for model in get_page_models():
        post_save.connect(synchronize_trees, sender=model)
        pre_delete.connect(synchronize_deletions, sender=model)
