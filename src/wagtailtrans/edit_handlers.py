# flake8: noqa
from django import forms
from django.template import Context, Template
from django.utils.safestring import mark_safe


class ReadOnlyWidget(forms.Select):
    """
    Render the original field as a hidden widget.
    And create a text display for the label
    """
    def __init__(self, text_display, *args, **kwargs):
        self.text_display = text_display
        self.initial_widget = forms.HiddenInput()
        super(ReadOnlyWidget, self).__init__(*args, **kwargs)

    def render(self, *args, **kwargs):
        original_content = self.initial_widget.render(*args, **kwargs)

        return mark_safe("""<span class="hidden">%s</span>%s""" % (
            original_content, self.text_display))


class CanonicalPageWidget(forms.Select):
    """Add a link to the canonical page, for ease of use."""

    def __init__(self, canonical_page, *args, **kwargs):
        self.canonical_page = canonical_page
        self.initial_widget = forms.HiddenInput()
        super(CanonicalPageWidget, self).__init__(*args, **kwargs)

    def render(self, *args, **kwargs):
        original_content = self.initial_widget.render(*args, **kwargs)
        template = Template("""
            {% load i18n %}
            <span class="hidden">{{ original_content }}</span>

            {% if canonical_page %}
                <a href="{% url 'wagtailadmin_pages:edit' canonical_page.id %}">{{ canonical_page.title }}</a>
            {% else %}
                {% trans "None" %}
            {% endif %}
        """)
        return mark_safe(template.render(Context({
            'canonical_page': self.canonical_page,
            'original_content': original_content,
        })))

