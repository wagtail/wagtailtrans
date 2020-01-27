import pytest

from tests.factories import sites
from wagtailtrans.edit_handlers import CanonicalPageWidget, ReadOnlyWidget
from wagtailtrans.models import Language


@pytest.mark.django_db
class TestEditHandlers:

    def setup(self):
        self.default_language = Language.objects.get(code='en')
        pages = sites.create_site_tree(language=self.default_language)
        self.last_page = pages[-1]

    def test_readonly_widget(self):
        widget = ReadOnlyWidget(text_display='Readonly Label')
        widget_contents = widget.render(name='English', value='en')
        assert 'name="English"' in widget_contents
        assert 'type="hidden"' in widget_contents

    def test_canonicalpage_widget(self):
        widget = CanonicalPageWidget(canonical_page=self.last_page)
        widget_contents = widget.render(name="Last Page", value="lstp")
        assert 'name="Last Page"' in widget_contents
        assert 'type="hidden"' in widget_contents
