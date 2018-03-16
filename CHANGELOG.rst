Changelog
=========

2.0.0 (16-03-2018)
------------------

 - Dropped support for Python 2
 - Dropped support for Wagtail versions earlier than 2.0
 - Dropped support for Django versions earlier than 1.11
 - Refactor .py files to line length 119
 - Changed the version number to be inline with Wagtail


0.2.0 (25-10-2017)
------------------

 - Dropped support for Wagtail versions earlier than 1.12
 - Custom ``get_admin_display_title`` method now uses Wagtails ``draft_title``
 - Fix: Get default language when ``languages_per_site`` is enabled now returns the correct default language for the site.


0.1.5 (27-08-2017)
------------------

 - Added `appveyor` to the CI to ensure MSSQL compatibility
 - Added a settings example file to the sandbox environment to ease the contribution setup
 - Added documentation on ``Contributing to Wagtailtrans``
 - Fix: language admin view throwing an exception with ``WAGTAILTRANS_LANGUAGES_PER_SITE`` set to ``True``


0.1.4 (03-07-2017)
------------------

 - Add support for ``Wagtail 1.11``
 - Update language selector templatetag to work with pages without language as well
 - Update language selector to order language selector based on language positions


0.1.3 (21-04-2017)
------------------

 - Add ``include_self=False`` kwarg to ``TranslatablePage.get_translations()`` to have the page return itself as well
 - Add language selector template tags
 - Update ``Language`` management to make use of ``wagtail.contrib.modeladmin``
 - Update ``Tox`` and ``Travis`` test matrix to include ``Wagtail 1.10`` support


0.1.2 (15-03-2017)
------------------
This release drops support for wagtail 1.6 and adds support for wagtail 1.8 and 1.9

 - Add new ``wagtailtrans`` logo.
 - Add admin view for translating with ``WAGTAILTRANS_SYNC_TREE = False``, prevents issues with not having a ``_meta`` on the ``TranslationForm``.
 - Update ``TranslationMiddleware`` to also use the ``Accept-Language`` HTTP header
 - Fix: Update middleware to prevent errors on empty database
 - Fix: backwards compatibility with Django 1.8 for ``wagtailtrans.templatetags``


0.1.1 (25-12-2016)
------------------

 - Add ``TranslationMiddleware`` for earlier language activation (replaces django ``LocaleMiddleware``)
 - Add ``language_id`` filter to ``wagtailtrans.models.TranslatablePage`` so search results can be filtered by language
 - Update documentation

0.1.0 Initial release (14-12-2016)
----------------------------------

 - Implement models following `Wagtail RFC9 <https://github.com/takeflight/wagtail-rfcs/blob/0008-translations/draft/0009-translations.rst>`_ by Tim Heap
 - Force language of child pages to language of parent
 - Support storing of translated pages
 - Support copying content of canonical pages when creating translations

 - Add translation information to the ``TranslatablePage.settings_panels``
 - Add dropdown page menu for adding translations
 - Add Language admin-UI in settings-menu
 - Add ``WAGTAILTRANS_SYNC_TREE`` setting to control which way trees behave
 - Add ``WAGTAILTRANS_TEMPLATE_DIR`` to override the admin template dir (pre Wagtail 1.8)
 - Add ``WAGTAILTRANS_LANGUAGES_PER_SITE`` setting to allow different page languages per site
 - Add SiteLanguages as SiteSetting in settings-menu (``WAGTAILTRANS_LANGUAGES_PER_SITE``)
 - Add ``wagtailtrans.models.TranslatablePage.get_admin_display_title`` to display the page language in the admin explorer (Wagtail 1.8+)
