from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, pre_delete
from wagtail.wagtailcore.models import Site, get_page_models

from wagtailtrans.models import Language, TranslatablePage
from wagtailtrans.permissions import (
    create_group_permissions, get_or_create_language_group)


def synchronize_trees(sender, instance, **kwargs):
    """synchronize the translation trees when
    a TranslatablePage is created.

    :param sender: Sender model
    :param instance: TranslatablePage instance
    :param kwargs: kwargs e.g. created

    """
    if (
        not kwargs.get('created') or
        not getattr(instance, 'language', False) or
        not instance.language.is_default
    ):
        return

    try:
        instance.get_site()
    except ObjectDoesNotExist:
        return

    for lang in Language.objects.filter(is_default=False):
        instance.create_translation(language=lang, copy_fields=True)


def synchronize_deletions(sender, instance, **kwargs):
    """We use pre_delete because when sync is disabled the foreign_key on
    canonical pages on_delete is set_null.

    :param sender: Sender model
    :param instance: TranslatablePage Instance
    :param kwargs: kwargs

    """
    language = getattr(instance, 'language', False)
    if language and not instance.canonical_page:
        instance.get_translations(only_live=False).delete()


def create_new_language_tree(sender, instance, **kwargs):
    """Signal will catch creation of a new language
    If sync trees is enabled it will create a whole new tree with
    correlating language.

    :param sender: Sender model
    :param instance: Language instance
    :param kwargs: kwargs e.g. created

    """
    if not kwargs.get('created'):
        return

    for site in Site.objects.all():
        site_pages = site.root_page.get_children().values_list('pk', flat=True)
        canonical_home_page = (
            TranslatablePage.objects
            .filter(pk__in=site_pages, language=Language.objects.default())
            .first())
        if not canonical_home_page:
            # no pages created yet.
            return
        descendants = canonical_home_page.get_descendants(inclusive=True)
        for child_page in descendants:
            child_page.specific.create_translation(instance, copy_fields=True)


def create_language_permissions_and_group(sender, instance, **kwargs):
    """Create a new `Translator` role with it's required permissions.

    :param sender: Sender model
    :param instance: Language instance
    :param kwargs: kwargs e.g. created

    """
    if not kwargs.get('created'):
        return

    group = get_or_create_language_group(instance)
    create_group_permissions(group, instance)


def register_signal_handlers():
    """Registers signal handlers.

    To create a signal for TranslatablePage we have to use wagtails
    get_page_model.

    """
    post_save.connect(create_language_permissions_and_group, sender=Language)

    if settings.WAGTAILTRANS_SYNC_TREE:
        post_save.connect(create_new_language_tree, sender=Language)

        for model in get_page_models():
            if hasattr(model, 'create_translation'):
                post_save.connect(synchronize_trees, sender=model)

            if hasattr(model, 'get_translations'):
                pre_delete.connect(synchronize_deletions, sender=model)
