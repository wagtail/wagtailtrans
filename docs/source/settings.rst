.. _settings:


========
Settings
========

There are a few settings which can be used to configure wagtailtrans to suit your needs, these settings need to be configured in your django settings module. All wagtailtrans settings are prefixed with ``WAGTAILTRANS_`` to avoid conflicts with other packages used.


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

If set to ``True`` wagtailtrans will allow you to define a default language and additional languages per site. This is mostly used in a ``multi site`` setup and allowes you to define the languages per site, this way they can differ for all available sites.
