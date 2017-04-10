.. _templatetags:

============
Templatetags
============

Wagtailtrans has a couple of template tags available to make linking in between pages more easy.
The template tags can be loaded from ``wagtailtrans_tags``:

.. code-block:: template

    {% load wagtailtrans_tags %}


Both template tags are configurable via the same keyword arguments.

``homepage_fallback``
---------------------

:Default: True

By default the template tag will fallback to a homepage if the linked page isn't publlished in
the other language(s). This setting will allow you to disable that behavior and leave the page
out of the returned result.


``include_self``
----------------

:Default: True

If set to ``False`` the requested page won't be included in the result.



-----------------------------
get_translations (assignment)
-----------------------------

The assignment tag will return a dictionary with language objects as keys and pages as values.
For example this can be used to render ``<link rel="alternate">`` tags.


.. code-block:: html

    {% get_translations page homepage_fallback=False include_self=False as translations %}

    {% for language, page in translations.items %}
    <link rel="alternate" href="{{ page.full_url }}" hreflang="{{ language.code }}">
    {% endfor %}


------------------------------------
render_language_selector (inclusion)
------------------------------------

This template tag will render a language selector, which renders the template located at:
``wagtailtrans/templatetags/language_selector.html``
