.. _migrating:


==================================
Migrate your existing Wagtail site
==================================

Migrating of already existing Wagtail content to ``Wagtailtrans`` can be quite difficult.
Since there is no way to do this automatically, we've put some examples below to point you in the right direction.

.. danger::
    Examples below contain custom database migrations, make sure you've created a back-up of your database before you start this migration process.


---------------------
Non Wagtailtrans site
---------------------

1. Install wagtailtrans

.. code-block:: bash

    $ pip install wagtailtrans

2. Add wagtailtrans to ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'wagtailtrans',
        # ...
    ]

3. Add ``wagtailtrans.models.TranslatablePage`` to the existing ``wagtail.wagtailcore.models.Page`` models.

.. code-block:: python

    from wagtail.wagtailcore.models import Page
    from wagtailtrans.models import TranslatablePage


    class HomePage(TranslatablePage, Page):
        # ...


4. Create a database migration file, when ``makemigrations`` is asking for a one-off default value for ``translatablepage_ptr`` you can fill in a fake value, since we're going to change this later.

.. code-block:: bash

    $ python manage.py makemigrations <appname>


5. Update migrations file to add the newly ``translatablepage_ptr_id`` field in the required table.

.. note::
    We've made some assumptions when creating this migration file, for example a default language ``en``. Please make sure you've checked all the database queries and adjusted them according to your own setup before executing.

.. code-block:: python

    class Migration(migrations.Migration):

        dependencies = [
            ('wagtailtrans', '0006_auto_20161212_2020'),
            ('pages', '0002_auto_20160930_1042'),
        ]

        operations = [
            migrations.RunSQL(
                """
                BEGIN;

                -- Remove constraints so we can edit our table
                ALTER TABLE pages_homepage DROP CONSTRAINT pages_homepage_pkey CASCADE;

                -- Add ``translatablepage_ptr_id`` field and copy the ``page_ptr_id`` content
                ALTER TABLE pages_homepage ADD COLUMN translatablepage_ptr_id INTEGER UNIQUE;
                UPDATE pages_homepage SET translatablepage_ptr_id=page_ptr_id;

                -- Insert the required values in ``wagtailtrans`` table
                INSERT INTO wagtailtrans_language (code, is_default, position, live) SELECT 'en', 't', 0, 't' WHERE NOT EXISTS (SELECT code FROM wagatailtrans_language WHERE code='en');
                INSERT INTO wagtailtrans_translatablepage (translatable_page_ptr_id, canonical_page_id, language_id) SELECT translatablepage_ptr_id, NULL, 1 FROM pages_homepage;

                -- Add required indexes and constraints
                ALTER TABLE pages_homepage ADD CONSTRAINT pages_homepage_translatablepage_ptr_id_e5b77cf7_fk_wagtailtrans_translatable_page_id FOREIGN KEY (translatablepage_ptr_id) REFERENCES wagtailtrans_translatablepage (translatable_page_ptr_id) DEFERRABLE INITIALLY DEFERRED;
                ALTER TABLE pages_homepage ALTER COLUMN translatablepage_ptr_id SET NOT NULL;
                ALTER TABLE pages_homepage ADD PRIMARY KEY (translatablepage_ptr_id);

                COMMIT;
                """,
                state_operations=[
                    migrations.AddField(
                        model_name='homepage',
                        name='translatablepage_ptr',
                        field=models.OneToOneField(auto_created=True on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailtrans.TranslatablePage'),
                        preserve_default=False,
                    ),
                    migrations.AlterField(
                        model_name='homepage',
                        name='page_ptr',
                        field=models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, to='wagtailcore.Page'),
                    ),
                ]
            ),
        ]


-------------------------
Pre 0.1 Wagtailtrans site
-------------------------

Before the 0.1 final release we've made a backwards incompatible change by defining a custom `parent_link <https://docs.djangoproject.com/en/1.8/topics/db/models/#specifying-the-parent-link-field>`_, this is done to ease the process of migrate an existing Wagtail site to Wagtailtrans.

Migrating can be done by following these steps:

1. Update code where necessary, models inheriting from ``wagtailtrans.models.TranslatablePage`` should also inherit from ``wagtail.wagtailcore.models.Page``

.. code-block:: python

    from wagtail.wagtailcore.models import Page
    from wagtailtrans.models import TranslatablePage


    class HomePage(TranslatablePage, Page):
        # ....


2. Create a database migration file, when ``makemigrations`` is asking for a one-off default value for ``page_ptr`` you can fill in a fake value, since we're going to change this later.

.. code-block:: bash

    $ python manage.py makemigrations <appname>


3. Alter the migration file to add the ``page_ptr_id`` field to the database, update it with the right values, create the required indexes and constraints and update the ORM state with a seperate state operation.

.. note::
    We've made some assumptions when creating this migration file. Please make sure you've checked all the database queries and adjusted them according your own setup before executing.

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
