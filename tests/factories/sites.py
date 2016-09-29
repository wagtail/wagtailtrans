import factory
from wagtail.wagtailcore.models import Site

from tests.factories.pages import TranslatedPageFactory


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
