.PHONY: devinstall test unittests coveragetests flaketest doctest ansibletest

devinstall:
	pip install --upgrade --upgrade-strategy eager -r requirements-dev.txt
	conda install --quiet --yes --file provisioning/roles/publicdb/files/conda.list
	pip install -r provisioning/roles/publicdb/files/pip.list

test: coveragetests flaketest doctest ansibletest

unittests:
	coverage run ./manage.py test tests

coveragetests: unittests
	coverage report

flaketest:
	flake8

doctest:
	PYTHONPATH=$(CURDIR):$(PYTHONPATH) sphinx-build -anW doc doc/_build/html

ansibletest:
	ansible-lint -p provisioning/playbook.yml || true
