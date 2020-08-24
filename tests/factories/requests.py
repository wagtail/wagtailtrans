from django.conf import settings
from django.test import RequestFactory as BaseRequestFactory

from .sites import SiteFactory
from .users import UserFactory


class RequestFactory(BaseRequestFactory):
    def request(self, user=None, **request):
        request = super().request(**request)
        # Backwards-compatible lookup for the deprecation of Wagtails SiteMiddleware per 2.9
        if 'wagtail.core.middleware.SiteMiddleware' in settings.MIDDLEWARE:
            request.site = SiteFactory()
        request.user = UserFactory()
        return request
