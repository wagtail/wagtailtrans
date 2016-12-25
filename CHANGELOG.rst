Changelog
=========

0.1.1 (25-12-2016)
------------------

 - Add ``TranslationMiddleware`` for earlier language activation (replaces django ``LocaleMiddleware``)
 - Add ``language_id`` filter to ``wagtailtrans.models.TranslatablePage`` so search results can be filterd by language
 - Update documentation

0.1.0 (14-12-2016)
------------------

Initial release
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
