default: develop

clean:
	find . -name '*.pyc' | xargs rm
	find . -name '*.egg-info' | xargs rm -rf

develop: clean requirements
	wagtailtrans.py migrate

requirements:
	pip install --upgrade -e .
	pip install --upgrade -e .[test]

qt:
	py.test -q --reuse-db wagtail/wagtailtrans/tests --tb=short

coverage:
	coverage run --source wagtail/wagtailtrans -m py.test -q --reuse-db --tb=short wagtail/wagtailtrans/tests
	coverage report -m

lint:
	flake8 wagtail

isort:
	isort `find . -name '*.py' -not -path '*/migrations/*'`
