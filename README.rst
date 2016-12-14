.. image:: https://travis-ci.org/LUKKIEN/wagtailtrans.svg?branch=master
    :target: https://travis-ci.org/LUKKIEN/wagtailtrans
    :alt: Build status

.. image:: https://coveralls.io/repos/github/LUKKIEN/wagtailtrans/badge.svg?branch=master
    :target: https://coveralls.io/github/LUKKIEN/wagtailtrans?branch=master
    :alt: Code coverage

.. image:: https://badge.fury.io/py/wagtailtrans.svg
    :target: https://badge.fury.io/py/wagtailtrans
    :alt: PyPi version

.. image:: https://readthedocs.org/projects/wagtailtrans/badge/?version=latest
    :target: http://wagtailtrans.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status


Wagtail multilanguage module
============================

Support multiple languages for your Wagtail site.

Requirements
------------

 - Python 2.7+
 - Django 1.8+
 - Wagtail 1.6+


Documentation
-------------

Project documentation can be found on `Read the Docs <http://wagtailtrans.readthedocs.io/>`_


Getting started
---------------

1. To install wagtailtrans, run this command in your terminal:

.. code-block:: console
    pip install wagtailtrans

2. Add ``wagtailtrans`` to your INSTALLED_APPS

3. Perform a migration

.. code-block:: console
    python manage.py migrate wagtailtrans``

You're set!


Settings
--------

Wagtailtrans can be configured to suit your needs, following settings are available:

 - ``WAGTAILTRANS_SYNC_TREE`` _(default: ``True``)_ configure the module to keep your language trees sychronized.
 - ``WAGTAILTRANS_LANGUAGES_PER_SITE`` _(default: ``False``)_ allow different languages per site (multi site setup)
