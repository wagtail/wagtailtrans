from __future__ import absolute_import, unicode_literals

from django.db import models

from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailtrans.models import (
    AbstractTranslationIndexPage, TranslatedPage)


class HomePage(TranslatedPage):
    body = RichTextField(
        blank=True,
        default="",
    )
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = TranslatedPage.content_panels + [
        FieldPanel('body'),
        ImageChooserPanel('image')
    ]

    subpage_types = ['HomePage']


class TranslationHomePage(AbstractTranslationIndexPage):
    subpage_types = ['HomePage']
