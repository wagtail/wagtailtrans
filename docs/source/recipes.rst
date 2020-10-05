.. _recipes:


===============
Recipes
===============

Code recipes that you may find useful.

-------------------------
Translate an external app
-------------------------

1. Create an abstract class from "TranslatablePage":

.. code-block:: python

    from wagtailtrans.models import TranslatablePage

    class TranslatablePageAbstract(TranslatablePage):
        class Meta:
            abstract = True

This code can reside in a separate app (let's call it "common"). It will be imported when needed by other apps.


2. Subclass from "TranslatablePageAbstract" and the external app pages.

Example for `puput <https://github.com/APSL/puput>`_:

.. code-block:: python

    from wagtail.core.models import Page
    from common.models import TranslatablePageAbstract
    from puput.models import BlogPage, EntryPage

    class BlogHomePage(TranslatablePageAbstract, BlogPage):
        subpage_types = ['blog.BlogEntryPage']

        search_fields = BlogPage.search_fields + TranslatablePageAbstract.search_fields[len(Page.search_fields):]
        settings_panels = BlogPage.settings_panels + TranslatablePageAbstract.settings_panels[len(Page.settings_panels):]

    class BlogEntryPage(TranslatablePageAbstract, EntryPage):
        parent_page_types = ['blog.BlogHomePage']

        search_fields = EntryPage.search_fields + TranslatablePageAbstract.search_fields[len(Page.search_fields):]
        settings_panels = EntryPage.settings_panels + TranslatablePageAbstract.settings_panels[len(Page.settings_panels):]


.. note::

    **settings_panels** and **search_fields** are the only attributes that might be defined in **both** wagtailtrans page model and the external app page models.
    To avoid overriding their external app definitions we redefine them here by adding the fields coming from the external app and the fields from wagtailtrans.
    You notice also that we avoided duplication of the common fields (Ex: Go live date, Expiry date) coming from the parent class "Page".
