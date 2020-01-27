.. _contributing:

Contributing to Wagtailtrans
============================

Thank you for considering contributing to Wagtailtrans.

We appreciate all kinds of support, whether it’s on bug reports, code,
documentation, tests or feature requests.

Issues
------

Our Github `issue tracker <https://github.com/wagtail/wagtailtrans/issues>`_ is the preferred channel for bug reports, feature requests and submitting pull requests. When creating new issues please provide as much relevant context as possible. Even your detailed comments on existing issues are a big help.

Pull request
------------

You can contribute your code by creating a new pull request. If there are any open issues you think you can help with, you can discuss it on that specific issue and start working on it. If you have any idea for a new feature, please raise it as an issue. Once a core contributor has responded and is happy with your idea and the solution, you can start coding.

You should create your `own fork <https://help.github.com/articles/fork-a-repo/>`_ of Wagtailtrans. We recommend you to create separate branches to keep all related changes within the same branch. Once you are done with your changes, you can submit a pull request for review.

**Please keep in mind**

* Any new feature must be documented.

* New features and bugfixes should have corresponding unit tests.

* If you're not already on the list, add your name to ``CONTRIBUTORS.md``.


Development
-----------

Wagtailtrans made it very easy to setup a runnable Django project to help with the development. It ships with a Sandbox application that can be availed for this purpose. You need to have some additional packages installed and a PostgreSQL Database on your local machine.

* **Get the codebase**

  Get a copy of the `Wagtailtrans codebase <https://github.com/wagtail/wagtailtrans>`_. Create your own fork and make changes there. For a brief, take a look at this `guideline <https://guides.github.com/activities/forking/>`_.

\

* **Setup database**

  Copy ``tests/_sandbox/settings/local_settings.sample`` to ``tests/_sandbox/settings/local_settings.py`` if you would like to use different database settings then we use in our default Sandbox application. This way you can setup your own `database settings for Django <https://docs.djangoproject.com/en/1.10/ref/settings/#databases>`_.

* **Setup local development server**

  1. Activate your virtual environment.

  2. Run following command :

      .. code-block:: bash

          $ make sandbox

    This will install required packages and run the initial data migrations.

* **Run locally**

  .. code-block:: bash

    $ ./manage.py runserver

Testing
-------

We use `pytest <https://docs.pytest.org/en/latest/>`_ for unit testing. To execute the full testsuite, run:

.. code-block:: bash

    $ make qt

or for a specific file:

.. code-block:: bash

    $ py.test path/to/file

If you want to measure test coverage you can run:

.. code-block:: bash

    $ make coverage

Wagtailtrans supports multiple environments which can be tested with ``tox``. It takes a bit longer to complete, but you can run it by a simple command: (Please make sure you have a setup with `multiple versions of python <http://blog.pinaxproject.com/2015/12/08/how-test-against-multiple-python-versions-parallel/>`_, in order to run this command.)

.. code-block:: bash

    $ tox
