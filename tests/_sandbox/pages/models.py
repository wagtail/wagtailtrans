from django.db import models
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel

from wagtailtrans.models import TranslatablePage


class HomePage(TranslatablePage):
    """An implementation of TranslatablePage."""

    subtitle = models.CharField(max_length=255, help_text="A required field, for test purposes")
    body = RichTextField(blank=True, default='')
    image = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')

    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('body'),
        ImageChooserPanel('image')
    ]

    subpage_types = ['HomePage']


class Article(Page):
    date = models.DateField()
    language = models.ForeignKey('wagtailtrans.Language', on_delete=models.SET_NULL, null=True)
    intro_text = RichTextField()

    content_panels = [
        FieldPanel('title', 'full title'),
        FieldPanel('date'),
        FieldPanel('intro_text'),
        FieldPanel('language'),
    ]
