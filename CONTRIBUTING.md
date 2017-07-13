# Contributing to Wagtailtrans

Thank you for considering to help `wagtailtrans`.

We appreciate all kinds of support, whether it's on bug reports, code, documentation, tests or feature requests.


## Issue tracker

The Github [issue tracker](https://github.com/LUKKIEN/wagtailtrans/issues) is the preferred channel for bug reports,
feature requests and submitting pull-requests. Please don't use this for support of any kind.


## Code reviews

The more the merrier, together we can create better than awesome software, so please feel free to join the process.

## Code contributions

You can contribute your code via creating new pull requests. If there are any open issues you think you can help with, you can discuss it on that specific issue and start working on it. If you have any idea for a new feature, please raise it as an issue. Once a core contributor has responded and is happy with your idea and the solution, you can start coding.

You should create your [own fork](https://help.github.com/articles/fork-a-repo/) of `wagtailtrans`. We recommend you to create separate branches to keep all related changes within the same branch. Once you are done with your changes, you can submit a pull request for review.

#### Pull request should include
* Any new feature must be documented.

* It is very important that for new features, you add additional unit tests, to test what you've written. They should be readable and test the correct things. For better code coverage, please make sure you cover as many lines of your code as possible within the unit tests.

* And obviously, if you're not already on the list, add your name to `CONTRIBUTORS.md`.

#### Setup locally for Development

_(\*Instructions are Mac only\*)_

`wagtailtrans` made it very easy to setup a runnable Django project to help with the development. It ships with a Sandbox application that can be availed for this purpose. You need to have some additional packages installed and a PostgreSQL Database on your local machine.

* We suggest you use a _**virtual environment**_ for development.

* Activate your virtual environment and install following packages.
```
    Django
    Wagtail
    psycopg2
    pytest
    pytest-cov
    pytest-django
    coverage
    factory-boy
```

* Set PostgreSQL Database Authentication parameters Host, User, and Password as environment variables.
```bash
export POSTGRES_HOST=host
export POSTGRES_USER=User
export POSTGRES_PASSWORD=password
```
You can also set optional `POSTGRES_DB` variable. Otherwise, it will create a database named `wagtailtrans_sandbox`.  Make sure your database user has sufficient permission to create databases because `wagtailtrans` need to create a database for testing.

#### Testing Locally

We Use [pytest](https://docs.pytest.org/en/latest/) for our testing. To execute full tests, run:

```bash
make qt
```
or for a specific file
```bash
py.test path/to/file
```

If you want to measure test coverage you can run:
```bash
make coverage
```

Wagtailtrans support Multi-environment tests and is configured to use `tox`. It takes a bit longer to complete, but you can run it by a simple command:
```bash
tox
```

## Code of conduct

In the interest of fostering an open and welcoming environment, we as contributors and maintainers pledge to
making participation in our project and our community a harassment-free experience for everyone, regardless of
age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal
appearance, race, religion, or sexual identity and orientation.

Please follow the guidelines of [Contributor Covenant Code of Conduct v1.4](http://contributor-covenant.org/version/1/4/)
