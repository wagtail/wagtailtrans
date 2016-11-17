import logging

from django.utils.deprecation import MiddlewareMixin

from .models import SiteLanguages
from .thread import set_site_languages

logger = logging.getLogger(__name__)


class SiteLanguagesMiddleware(MiddlewareMixin):
    """Make sure the SiteSetting object is loaded in the thread."""

    def process_request(self, request):
        if not request.site:
            logger.error("No site configured for request.")

        site_languages = SiteLanguages.for_site(request.site)
        if site_languages:
            set_site_languages(site_languages)
