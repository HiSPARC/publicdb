.PHONY: test flaketest doctest ansibletest

test: flaketest doctest ansibletest

flaketest:
	flake8

doctest:
	PYTHONPATH=$(CURDIR):$(PYTHONPATH) sphinx-build -anW doc doc/_build/html

ansibletest:
	ansible-lint -p provisioning/playbook.yml || true
