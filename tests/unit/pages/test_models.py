import pytest
from django.http import HttpRequest
from wagtail.core.models import Site


@pytest.mark.django_db
class TestHomePage:

    def test_get(self, rf, languages, sites):
        site = sites.get(hostname='es.localhost')

        request = HttpRequest()
        request.path = '/'
        request.META['HTTP_HOST'] = 'es.localhost'
        request.META['SERVER_PORT'] = 8000

        assert Site.find_for_request(request) == site
