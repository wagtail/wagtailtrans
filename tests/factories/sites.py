import factory
from wagtail.wagtailcore.models import Site

from tests.factories.pages import HomePageFactory, TranslatableSiteRootFactory


class SiteFactory(factory.DjangoModelFactory):
    hostname = 'localhost'
    port = 8000
    site_name = 'TestSite'
    root_page = factory.SubFactory(TranslatableSiteRootFactory)
    is_default_site = True

    class Meta:
        model = Site


def create_site_tree(language, site=None, *items, **homepage_kwargs):
    if not items:
        items = ['%s homepage' % language.code, 'subpage1', 'subpage2']

    if not site:
        site = SiteFactory()

    root_page = site.root_page

    pages = [root_page]
    for item in items:
        page = HomePageFactory.build(
            language=language, title=item, **homepage_kwargs)
        pages[-1].add_child(instance=page)
        pages.append(page)

    return pages
