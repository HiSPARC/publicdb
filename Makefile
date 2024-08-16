.PHONY: devinstall
devinstall:
	pip install --upgrade --upgrade-strategy eager -r requirements-dev.txt
	conda install --quiet --yes --channel conda-forge --file requirements-conda.txt
	pip install -r requirements.txt

.PHONY: test
test: coveragetests linttest doctest ansibletest

.PHONY: unittests
unittests:
	coverage run ./manage.py test --shuffle $(tests)

.PHONY: coveragetests
coveragetests: unittests
	coverage report

.PHONY: linttest
linttest:
	ruff check .
	typos .

.PHONY: doctest
doctest:
	PYTHONPATH=$(CURDIR):$(PYTHONPATH) sphinx-build -anW doc doc/_build/html

.PHONY: ansibletest
ansibletest:
	ansible-lint -p provisioning/playbook.yml || true
