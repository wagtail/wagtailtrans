#!/usr/bin/env python
from setuptools import find_packages, setup

tests_require = [
    'factory-boy==2.7.0',
    'flake8==3.0.4',
    'isort==4.2.5',
    'pytest==3.0.2',
]


setup(
    name='wagtail.wagtailtrans',
    version='0.0.1',
    description='A Wagtail add-on for supporting multilingual sites',
    author='Lukkien BV',
    author_email='support@lukkien.com',
    url='https://lukkien.com/',
    packages=find_packages(),
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
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ],
    install_requires=[
        'wagtail>=1.6,<1.7'
    ],
    tests_require=tests_require,
    extras_require={
        'test': tests_require
    },
    namespace_packages=['wagtail'],
    scripts=[
        'wagtail/wagtailtrans/tests/wagtailtrans.py',
    ]
)
