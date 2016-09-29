TAG = $(BUILD_NUMBER)
PROJECT = wagtailtrans-sandbox

default: develop

clean:
	@find . -name '*.pyc' | xargs rm
	@find src -name '*.egg-info' | xargs rm -rf

develop: clean requirements
	@python manage.py migrate

requirements:
	@pip install --upgrade -e .
	@pip install --upgrade -e .[test]

qt:
	@py.test -q --reuse-db tests/ --tb=short

coverage:
	@coverage run --source wagtailtrans -m py.test -q --reuse-db --tb=short tests
	@coverage report -m

lint:
	@flake8 wagtail

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

push: build
	docker tag $(PROJECT) registry.lukkien.com/$(PROJECT):$(TAG)
	docker push registry.lukkien.com/$(PROJECT):$(TAG)

deploy-test: push
	ssh deploy-lukkien@192.168.226.18 ./tools/docker/restart $(PROJECT) $(TAG)
