from setuptools import find_packages, setup

tests_require = [
    'coverage==4.2',
    'factory-boy==2.7.0',
    'flake8==3.0.4',
    'isort==4.2.5',
    'pytest==3.0.2',
    'pytest-django==3.0.0',
    'pytest-warnings==0.1.0',
    'psycopg2>=2.6',
]

setup(
    name='wagtailtrans',
    version='0.1.0b1',
    description='A Wagtail add-on for supporting multilingual sites',
    author='Lukkien BV',
    author_email='support@lukkien.com',
    url='https://lukkien.com/',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    license='BSD',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ],
    install_requires=[
        'wagtail>=1.6',
    ],
    tests_require=tests_require,
    extras_require={
        'test': tests_require
    }
)
