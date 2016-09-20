====================================
Page Translations support to Wagtail
====================================


Changes
~~~~~~~

- Implement models following RFC9
- Add Language admin-UI in settings-menu
- Support storing translated pages
- Add TAB for translations
- Add dropdown page menu for adding translations
- Support copying content of canonical page when creating translation
- Force language of child-pages to language of parent


=================
Mandatory setting
=================
Please define: WAGTAILTRANS_SYNC_TREE = True if you want to keep all
language trees synchronized. Use WAGTAILTRANS_SYNC_TREE = False to
disable sync and have free flowing trees.
