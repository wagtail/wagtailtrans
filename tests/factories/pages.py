import factory

from wagtailtrans import models
from tests.factories import language


class TranslatableSiteRootFactory(factory.DjangoModelFactory):
    title = 'Translatable Root'
    depth = 1
    path = '0001'

    class Meta:
        model = models.TranslatableSiteRootPage


class TranslatedPageFactory(factory.DjangoModelFactory):
    language = factory.SubFactory(language.LanguageFactory)
    title = 'Foo Bar'

    class Meta:
        model = models.TranslatablePage
