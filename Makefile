default: develop

clean:
	find . -name *.pyc | xargs rm
	find . -name *.egg-info | xargs rm -rf

develop: clean requirements
	wagtailtrans.py migrate

requirements:
	pip install --upgrade -e .
