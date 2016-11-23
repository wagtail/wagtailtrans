import pytest

from tests.factories.requests import RequestFactory
from wagtailtrans.middleware import SiteLanguagesMiddleware
from wagtailtrans.models import SiteLanguages


@pytest.mark.django_db
def test_middleware():
    """Verify that the sitelanguages attribute is set by the middleware."""
    middleware = SiteLanguagesMiddleware()
    rf = RequestFactory()
    request = rf.get('/')
    assert getattr(request.site, 'sitelanguages', None) is None
    middleware.process_request(request)
    assert isinstance(request.site.sitelanguages, SiteLanguages)
