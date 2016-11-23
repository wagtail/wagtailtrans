from django.test import RequestFactory as BaseRequestFactory

from .sites import SiteFactory


class RequestFactory(BaseRequestFactory):
    def request(self, user=None, **request):
        request = super(RequestFactory, self).request(**request)
        request.site = SiteFactory()

        return request
