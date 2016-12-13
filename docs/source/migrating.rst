:tocdepth: 2

.. _migrating:


Migrate your existing Wagtail site
==================================

Migrating of already existing Wagtail content to ``Wagtailtrans`` can be quite difficult.
Since there is no way to do this automatically, we've put some examples below to point you in the right direction.

*note: below examples contain custom database migrations*


Existing Wagtail site
---------------------

TODO:


Pre 0.1 Wagtailtrans site
-------------------------

Before the 0.1 final release we've made a backwards incompatible change by defining a custom [parent_link](https://docs.djangoproject.com/en/1.8/topics/db/models/#specifying-the-parent-link-field), this is done to allow users to easier migrate their existing Wagtail site to Wagtailtrans.

Migrating can be done by following these steps:

1. Update code where necessary, models inheriting from ``wagtailtrans.models.TranslatablePage`` should also inherit from ``wagtail.wagtailcore.models.Page``

.. code-block:: python

    from wagtail.wagtailcore.models import Page
    from wagtailtrans.models import TranslatablePage


    class ExtendedPage(TranslatablePage, Page):
        # ....


2. Create a database migration file

.. code-block:: bash

    $ python manage.py makemigrations <appname>


3. Alter the migration file to add the ``page_ptr_id`` field to the database, update it with the right values, create the required indexes and constraints and update the ORM state with a seperate state operation.

.. code-block:: python

    class Migration(migrations.Migration):

        dependencies = [
            ('wagtailcore', '0029_unicode_slugfield_dj19'),
            ('pages', '0002_auto_20160930_1042'),
            ('wagtailtrans', '0006_auto_20161212_2020'),
        ]

        operations = [
            migrations.RunSQL(
                """
                BEGIN;

                -- Add the ``page_ptr_id`` field in the DB.
                ALTER TABLE pages_homepage ADD COLUMN page_ptr_id INTEGER UNIQUE;
                UPDATE pages_homepage SET page_ptr_id=translatablepage_ptr_id;
                ALTER TABLE pages_homepage ALTER COLUMN page_ptr_id DROP DEFAULT;
                ALTER TABLE pages_homepage ALTER COLUMN page_ptr_id SET NOT NULL;
                ALTER TABLE pages_homepage ADD CONSTRAINT pages_homepage_page_ptr_id_5b805d74_fk_wagtailcore_page_id FOREIGN KEY (page_ptr_id) REFERENCES wagtailcore_page (id) DEFERRABLE INITIALLY DEFERRED;

                COMMIT;
                """,
                state_operations=[
                    migrations.AddField(
                        model_name='homepage',
                        name='page_ptr',
                        field=models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, to='wagtailcore.Page'),
                        preserve_default=False,
                    ),
                ]
            ),
        ]
