from wagtail.contrib.wagtailsitemaps.sitemap_generator import Sitemap


class MultilanguageSitemap(Sitemap):
    template = 'wagtailtrans/sitemaps/sitemap.xml'
