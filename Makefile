.PHONY: test flaketest doctest

test: flaketest doctest

flaketest:
	flake8 --ignore=Z --exclude=urls.py,tests.py,*/migrations/ publicdb

doctest:
	PYTHONPATH=$(CURDIR):$(PYTHONPATH) sphinx-build -anW doc doc/_build/html
