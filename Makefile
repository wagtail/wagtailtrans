PROJECT = wagtailtrans-sandbox

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


# Docker commands
package:
	python setup.py sdist

build: package
	docker build -t $(PROJECT) .

run: build
	docker run --name $(PROJECT) -d -P -p 8000:80 $(PROJECT)

ssh:
	docker exec -it $(PROJECT) /bin/bash
