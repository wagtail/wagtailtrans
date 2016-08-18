from __future__ import unicode_literals

import uuid

from django.db import models
from django.http import Http404
from django.shortcuts import redirect
from django.utils.translation import activate
from wagtail.wagtailcore.models import Page


class Language(models.Model):
    code = models.CharField(
        max_length=12,
        help_text="One of the languages defined in LANGUAGES"
    )
    is_default = models.BooleanField(
        default=False, help_text="""
        Visitors with no language preference will see the site in
        this language
        """)
    order = models.IntegerField(
        help_text="""
        Language choices and translations will be displayed in this
        order
        """)
    live = models.BooleanField(
        default=True,
        help_text="Is this language available for visitors to view?"
    )

    class Meta:
        ordering = ['order']


class TranslatedPage(Page):

    translated_page_ptr = models.OneToOneField(
        'TranslatedPage',
        parent_link=True, related_name='+',
        null=True, on_delete=models.SET_NULL,
    )
    translation_key = models.UUIDField(db_index=True, default=uuid.uuid4)

    language = models.ForeignKey(Language, on_delete=models.PROTECT)

    class Meta:
        unique_together = [
            ('translation_key', 'language'),
        ]

    def serve(self, request, *args, **kwargs):
        activate(self.language.code)
        super(TranslatedPage, self).serve(request, *args, **kwargs)


def get_user_languages(request):
    return Language.objects.all()


class AbstractTranslationIndexPage(Page):
    def serve(self, request):
        languages = get_user_languages(request)
        candidate_pages = TranslatedPage.objects\
            .live().specific()\
            .child_of(self)
        for language in languages:
            try:
                translation = candidate_pages.filter(
                    language=language).get()
                return redirect(translation.url)
            except TranslatedPage.DoesNotExist:
                continue
        raise Http404

    class Meta:
        abstract = True
