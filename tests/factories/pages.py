import factory
from wagtail.wagtailcore.models import Page

from wagtailtrans import models
from tests.factories import language


class TranslatableSiteRootFactory(factory.DjangoModelFactory):
    title = 'translatable-site-root'
    depth = 2

    class Meta:
        model = models.TranslatableSiteRootPage

    @classmethod
    def _create(cls, *args, **kwargs):
        try:
            root = Page.objects.get(depth=0)
        except Page.DoesNotExist:
            root = Page.add_root(title='root')

        return root.add_child(title=kwargs['title'])


class TranslatablePageFactory(factory.DjangoModelFactory):
    language = factory.SubFactory(language.LanguageFactory)
    title = 'Foo Bar'

    class Meta:
        model = models.TranslatablePage
