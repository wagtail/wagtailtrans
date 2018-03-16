import os
import sys

from setuptools import find_packages, setup

PROJECT_DIR = os.path.dirname(__file__)

sys.path.append(os.path.join(PROJECT_DIR, 'src'))
from wagtailtrans import get_version  # noqa isort:skip

sandbox_require = [
    'Django>=2.0',
    'Wagtail>=2.0',
    'psycopg2>=2.5.4',
    'djangorestframework>=3.7',
]

docs_require = [
    'sphinx',
    'sphinx_rtd_theme',
]

tests_require = [
    # Required for test and coverage
    'pytest',
    'pytest-cov',
    'pytest-django',
    'coverage',
    'factory-boy',
    'psycopg2>=2.5.4',
    # Linting
    'flake8',
    'isort',
]

setup(
    name='wagtailtrans',
    version=get_version().replace(' ', '-'),
    description='A Wagtail add-on for supporting multilingual sites',
    author='Lukkien BV',
    author_email='support@lukkien.com',
    url='https://lukkien.com/',
    extras_require={
        'test': tests_require,
        'doc': docs_require,
        'sandbox': sandbox_require + tests_require + docs_require,
    },
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    license='BSD',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ]
)
