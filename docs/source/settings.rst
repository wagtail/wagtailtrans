.. _settings:


========
Settings
========

There are a few settings which can be used to configure wagtailtrans to suit
your needs, these settings need to be configured in your django settings module.
All wagtailtrans settings are prefixed with ``WAGTAILTRANS_`` to avoid conflicts
with other packages used.


``WAGTAILTRANS_SYNC_TREE``
--------------------------

:Default: ``True``

If set to ``False`` wagtailtrans will work with ``Freeform`` trees.

.. seealso::
    The documentation about :ref:`synchronized_trees`

.. seealso::
    The documentation about :ref:`freeform_trees`


``WAGTAILTRANS_LANGUAGES_PER_SITE``
-----------------------------------

:Default: ``False``

If set to ``True`` wagtailtrans will allow you to define a default language and
additional languages per site. This is mostly used in a ``multi site`` setup and
allowes you to define the languages per site, this way they can differ for all
available sites.

.. note::

    When using Django's loaddata wagtailtrans detaches all signals so there
    aren't any weird side-effects triggered when loading your data. However
    using loaddata in combination with ``WAGTAILTRANS_LANGUAGES_PER_SITE`` there
    is still one signal which can't be detached ``m2m_changed`` to do this you
    can provide the environment variable ``WAGTAILTRANS_DISABLE_SIGNALS=True`` to
    your loadddata command, this will skip adding the signals as well.

    Example:

        ``WAGTAILTRANS_DISABLE_SIGNALS=True ./manage.py loaddata data.json``


.. danger::

    Using ``WAGTAILTRANS_DISABLE_SIGNALS`` can potentially break your complete
    wagtailtrans installation, when used incorrectly.


``WAGTAILTRANS_HIDE_TRANSLATION_TREES``
---------------------------------------

:Default: ``False``

If set to ``True`` the CMS user will only see the tree of the canonical
language, with an ``edit in`` button where they can choose the language to edit
the page in.


``WAGTAILTRANS_NO_PREFIX_FOR_DEFAULT_LANGUAGE``
-----------------------------------------------

:Default: ``False``

If set to ``True`` wagtailtrans will allow user to access pages defined under
the default language tree without the language prefix.

.. note::

    Let's assume English as a default language and a ``TranslatablePage`` available
    under the following path - ``/en/news/``. With ``NO_PREFIX_FOR_DEFAULT_LANGUAGE``
    set to ``True`` the page will be available under ``/news/`` page as well.


``WAGTAILTRANS_REDIRECT_UNPREFIXED_PATHS``
------------------------------------------

:Default: ``False``

If set to ``True`` wagtailtrans will redirect all unprefixed paths to a prefixed version.

.. note::

    Let's assume English as the language selected by the user and a ``TranslatablePage``
    available under the following path - ``/en/news/``. With ``REDIRECT_UNPREFIXED_PATHS``
    set to ``True`` all requests to ``/news/`` will redirect user to ``/en/news/``.

.. note::

    If ``NO_PREFIX_FOR_DEFAULT_LANGUAGE`` is set to ``True`` as well as ``REDIRECT_UNPREFIXED_PATHS``
    there will be no redirection for the default langue.
