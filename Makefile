.PHONY: dist docs

default: help

define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean:
	@find . -name '*.pyc' | xargs rm -f
	@find src -name '*.egg-info' | xargs rm -rf

develop: clean requirements
	@python manage.py migrate

docs:  ## Create wagtailtrans Sphinx documentation
	@make -C docs/ html

requirements:
	@pip install --upgrade -e .

qt:
	@py.test -q --reuse-db tests/ --tb=short

coverage:
	@coverage run --source wagtailtrans -m py.test -q --reuse-db --tb=short tests
	@coverage report -m
	@coverage html
	$(BROWSER) htmlcov/index.html

lint:
	@flake8 src --exclude migrations

isort:
	isort --recursive src tests --skip migrations

dist: clean
	@python setup.py sdist bdist_wheel
	ls -l dist

release: dist
	twine upload -r lukkien dist/*

sandbox: clean
	@pip install -e .[sandbox]
	@python manage.py migrate
