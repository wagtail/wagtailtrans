from django.test import RequestFactory as BaseRequestFactory

from .sites import SiteFactory
from .users import UserFactory


class RequestFactory(BaseRequestFactory):
    def request(self, user=None, **request):
        request = super(RequestFactory, self).request(**request)
        request.site = SiteFactory()
        request.user = UserFactory()
        return request
