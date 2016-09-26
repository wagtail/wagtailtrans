import factory

from wagtail.wagtailtrans import models
from wagtail.wagtailcore.models import Site


class LanguageFactory(factory.DjangoModelFactory):
    order = 1
    code = 'en-gb'
    is_default = True
    live = True

    class Meta:
        model = models.Language


class TranslatedPageFactory(factory.DjangoModelFactory):
    language = factory.SubFactory(LanguageFactory)
    title = 'Foo Bar'
    depth = 0
    path = 'home/one'

    class Meta:
        model = models.TranslatedPage

    @classmethod
    def _create(cls, *args, **kwargs):
        try:
            return models.TranslatedPage.objects.get(title=kwargs['title'])
        except models.TranslatedPage.DoesNotExist:
            if kwargs['depth'] == 0:
                return args[0].add_root(**kwargs)
            else:
                raise NotImplementedError()


def create_page_tree(*items):
    """Shortcut to create a page tree 3 levels deep"""
    if not items:
        items = ['english homepage', 'subpage1', 'subpage2']

    rootpage = TranslatedPageFactory(title=items[0])
    for item in items[1:]:
        rootpage = rootpage.add_child(title=item)
    return rootpage


class SiteFactory(factory.DjangoModelFactory):
    hostname = 'localhost'
    port = 8000
    site_name = 'TestSite'
    root_page = factory.SubFactory(TranslatedPageFactory)
    is_default_site = True

    class Meta:
        model = Site


def create_site_tree(*items):
    site = SiteFactory()
    if not items:
        items = ['english homepage', 'subpage1', 'subpage2']

    rootpage = site.root_page
    for item in items:
        rootpage = rootpage.add_child(title=item)
    return rootpage
