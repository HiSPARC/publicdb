.PHONY: test flaketest doctest ansibletest

test: flaketest doctest ansibletest

flaketest:
	flake8 --ignore=Z --exclude=urls.py,tests.py,*/migrations/ publicdb

doctest:
	PYTHONPATH=$(CURDIR):$(PYTHONPATH) sphinx-build -anW doc doc/_build/html

ansibletest:
	ansible-lint -p provisioning/playbook.yml || true
