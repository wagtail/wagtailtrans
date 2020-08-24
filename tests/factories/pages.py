import factory
from wagtail.core.models import Page
from wagtail.images.tests.utils import get_image_model, get_test_image_file

from tests._sandbox.pages.models import HomePage
from tests.factories import language
from wagtailtrans import models


class TranslatableSiteRootFactory(factory.django.DjangoModelFactory):
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


class TranslatablePageFactory(factory.django.DjangoModelFactory):
    language = factory.SubFactory(language.LanguageFactory)

    class Meta:
        model = models.TranslatablePage

    @classmethod
    def _build(cls, *args, **kwargs):
        obj = super()._build(*args, **kwargs)
        if not obj.title:
            obj.title = "Page-{}".format(obj.language.code)
        return obj


class ImageFactory(factory.django.DjangoModelFactory):
    title = factory.Faker('word')
    file = get_test_image_file()

    class Meta:
        model = get_image_model()


class HomePageFactory(TranslatablePageFactory):

    class Meta:
        model = HomePage

    @classmethod
    def _build(cls, *args, **kwargs):
        obj = super()._build(*args, **kwargs)

        # Set an image if not present yet
        if not obj.image:
            obj.image = ImageFactory.create()

        # Set some other basic attributes
        for part in ('subtitle', 'body'):
            if not getattr(obj, part):
                setattr(obj, part, "{} {}".format(part, obj.language.code))
        return obj


class WagtailPageFactory(factory.django.DjangoModelFactory):
    depth = 0
    title = 'root'

    class Meta:
        model = Page
