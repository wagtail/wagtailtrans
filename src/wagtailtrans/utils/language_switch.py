from django.db import transaction
from django.db.models import Q

from wagtailtrans.models import Language, get_translatable_models


def create_new_canonical_page_mapping(new_language, queryset):
    return dict(queryset.filter(language_id=new_language.pk).values_list('canonical_page_id', 'pk'))


def get_page_queryset(model, site=None):
    if site is not None:
        return model.objects.descendant_of(site.root_page)

    return model.objects.all()


@transaction.atomic
def change_default_language(new_language, site=None):
    """Change the default language
    for the site or all sites if no site is given

    """
    if site is None:
        old_language = Language.objects.default()
        if old_language is not None:
            old_language.is_default = False
            old_language.save()

        new_language.is_default = True
        new_language.save()

    for model in get_translatable_models():
        queryset = get_page_queryset(model, site)
        mapping = create_new_canonical_page_mapping(new_language, queryset)

        # New canonical languages should not have a canonical page
        queryset.filter(pk__in=mapping.values()).update(canonical_page_id=None)

        for old_pk, new_pk in mapping.items():
            # Set new canonical page id to the new canonical pages.
            queryset.filter(Q(canonical_page_id=old_pk) | Q(pk=old_pk)).update(canonical_page_id=new_pk)
            # new canonical pages can't have a canonical page
            # so we set the canonical_page_id to None
            queryset.filter(pk=new_pk).update(canonical_page_id=None)
