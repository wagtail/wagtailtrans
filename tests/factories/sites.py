import factory
from wagtail.wagtailcore.models import Site

from tests.factories.pages import (TranslatableSiteRootFactory,
                                   TranslatedPageFactory)


class SiteFactory(factory.DjangoModelFactory):
    hostname = 'localhost'
    port = 8000
    site_name = 'TestSite'
    root_page = factory.SubFactory(TranslatableSiteRootFactory)
    is_default_site = True

    class Meta:
        model = Site


def create_site_tree(language, *items):
    if not items:
        items = ['english homepage', 'subpage1', 'subpage2']

    pages = []

    site = SiteFactory()
    root_page = site.root_page

    pages.append(root_page)

    for item in items:
        page = TranslatedPageFactory.build(language=language, title=item)
        pages[-1].add_child(instance=page)
        pages.append(page)

    return pages
