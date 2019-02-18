import factory

from wagtail.core.models import Site

from wagtailtrans import models

from tests.factories.language import LanguageFactory
from tests.factories.pages import HomePageFactory, MixinHomePageFactory, TranslatableSiteRootFactory


class SiteFactory(factory.DjangoModelFactory):
    hostname = 'localhost'
    port = 8000
    site_name = 'TestSite'
    root_page = factory.SubFactory(TranslatableSiteRootFactory)
    is_default_site = True

    class Meta:
        model = Site
        django_get_or_create = ['hostname']


def create_site_tree(language, site=None, *items, using_mixin=False, **homepage_kwargs):
    if not items:
        items = ['%s homepage' % language.code, 'subpage1', 'subpage2']

    if not site:
        site = SiteFactory()

    root_page = site.root_page

    pages = [root_page]
    homepage_factory = MixinHomePageFactory if using_mixin else HomePageFactory
    for item in items:
        page = homepage_factory.build(language=language, title=item, **homepage_kwargs)
        pages[-1].add_child(instance=page)
        pages.append(page)

    return pages


class SiteLanguagesFactory(factory.DjangoModelFactory):
    site = factory.SubFactory(SiteFactory)
    default_language = factory.SubFactory(LanguageFactory)

    class Meta:
        model = models.SiteLanguages
        django_get_or_create = ['site']
