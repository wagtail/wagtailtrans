import os
import sys

from setuptools import find_packages, setup

PROJECT_DIR = os.path.dirname(__file__)

sys.path.append(os.path.join(PROJECT_DIR, 'src'))
from wagtailtrans import get_version  # noqa isort:skip

install_requires = [
    'wagtail>=2.7,<2.12'
]

sandbox_require = [
    'Django>=3.1',
    'Wagtail>=2.11',
    'psycopg2-binary>=2.5.4',
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
    'psycopg2-binary>=2.5.4,<2.9',
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
    install_requires=install_requires,
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
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Framework :: Django',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Framework :: Wagtail',
        'Framework :: Wagtail :: 2',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ]
)
