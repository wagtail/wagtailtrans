.. wagtailtrans documentation master file, created by
   sphinx-quickstart on Tue Sep 20 14:54:40 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


=======================================
Welcome to wagtailtrans's documentation
=======================================

Wagtailtrans is a package that can be used to facilitate multi language sites in Wagtail. We developed wagtailtrans with two implementations in mind.

    - A **synchronised** tree
    - A **freeform** tree

Synchronised tree is a method used to keep the tree structure in all languages the same. Any changes in the tree of the default language will also automatically be done in the language tree(s).

.. seealso::
    The documentation about :ref:`synchronized_trees`


Freeform trees allows the customization of the language trees. Pages can still be copied with content into the preferred language but this is not automatic nor mandatory. moderators can decide how the page structure works for every language.

.. seealso::
    The documentation about :ref:`freeform_trees`


-----------------
Table of contents
-----------------

.. toctree::
   :maxdepth: 2

   getting_started
   migrating
   settings
   recipes
   reference/index
   releases/index
   contributing
