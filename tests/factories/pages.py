import factory
from wagtail.wagtailimages.tests.utils import (get_image_model,
                                               get_test_image_file)

from tests._sandbox.pages.models import HomePage
from tests.factories import language
from wagtailtrans import models


class TranslatableSiteRootFactory(factory.DjangoModelFactory):
    title = 'Translatable Root'
    depth = 1
    path = '0001'

    class Meta:
        model = models.TranslatableSiteRootPage


class TranslatedPageFactory(factory.DjangoModelFactory):
    language = factory.SubFactory(language.LanguageFactory)

    class Meta:
        model = models.TranslatablePage

    @classmethod
    def _build(cls, *args, **kwargs):
        obj = super(TranslatedPageFactory, cls)._build(*args, **kwargs)
        if not obj.title:
            obj.title = "Page ({})".format(obj.language.code)
        return obj


class ImageFactory(factory.DjangoModelFactory):
    title = factory.Faker('word')
    file = get_test_image_file()

    class Meta:
        model = get_image_model()


class HomePageFactory(TranslatedPageFactory):
    class Meta:
        model = HomePage

    @classmethod
    def _build(cls, *args, **kwargs):
        obj = super(HomePageFactory, cls)._build(*args, **kwargs)

        # Set an image if not present yet
        if not obj.image:
            obj.image = ImageFactory.create()

        # Set some other basic attributes
        for part in ('subtitle', 'body'):
            if not getattr(obj, part):
                setattr(obj, part, "{} {}".format(part, obj.language.code))
        return obj
