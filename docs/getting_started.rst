:tocdepth: 2

.. _getting_started:

Getting started with wagtailtrans
*********************************
To start using wagtailtrans in your project take the following steps.

installation
------------
using pip::

    pip install wagtailtrans


Add to installed apps::

    INSTALLED_APPS = [
    ...
    'wagtailtrans',
    ..
    ]

Define in your settings if you use synchronized trees::

    WAGTAILTRANS_SYNC_TREE = True

If you want to use freeform language trees use::

    WAGTAILTRANS_SYNC_TREE = False


Incorporating
-------------
To start using wagtailtrans we first need to create a translation home page.
This page will route the requests to the homepage in the right language.
We can create a translation site root page by creating the `TranslatableSiteRootPage` as the first page
under the root page.

We will also make a Home page which will be translatable.
This is done by extending your page from TranslatablePage instrad of wagtailscore's Page ::

    from wagtail.wagtailtrans.models import TranslatablePage

    class HomePage(TranslatablePage):
        body = RichTextField(
            blank=True,
            default="",
        )
        image = models.ForeignKey(
            'wagtailimages.Image',
            null=True,
            blank=True,
            on_delete=models.SET_NULL,
            related_name='+'
        )

        content_panels = TranslatablePage.content_panels + [
            FieldPanel('body'),
            ImageChooserPanel('image')
        ]
        # add more content as you please.

        subpage_types = ['HomePage', '......']

This creates our first translated page. To start using this we first need to migrate our database::

    python manage.py makemigrations
    python manage.py migrate

Now run the server and under Root create a TranslatableSiteRootPage (MySite).

Now we need to create a site and set our TranslationHomepage (MySite) as root page.

..  figure::  _static/Site.png
    :align:   center
    Create your site and select TranslationHomepage as root page.

We now have the basics for a Translated Site.

Synchronized trees
------------------
To start using syncronized trees, please see: :ref:`synchronized_trees`.

Freeflow trees
--------------
To start using freeform trees please see: :ref:`freeform_trees`.
