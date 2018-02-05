.PHONY: test unittests coveragetests flaketest doctest ansibletest

test: coveragetests flaketest doctest ansibletest

unittests:
	coverage run ./publicdb/manage.py test tests

coveragetests: unittests
	coverage report

flaketest:
	flake8

doctest:
	PYTHONPATH=$(CURDIR):$(PYTHONPATH) sphinx-build -anW doc doc/_build/html

ansibletest:
	ansible-lint -p provisioning/playbook.yml || true
