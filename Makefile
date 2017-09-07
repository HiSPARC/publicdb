.PHONY: gh-pages test

gh-pages:
ifeq ($(strip $(shell git status --porcelain | wc -l)), 0)
	git checkout gh-pages
	git rm -rf .
	git clean -dxf
	git checkout HEAD .nojekyll
	git checkout master doc publicdb
	make -C doc/ html
	make -C doc/ latexpdf
	mv -fv doc/_build/html/* .
	mv -fv doc/_build/latex/*.pdf .
	rm -rf doc/ publicdb/
	git add -A
	git commit -m "Generated gh-pages for `git log master -1 --pretty=short --abbrev-commit`"
	git checkout master
else
	$(error Working tree is not clean, please commit all changes.)
endif

test:
	flake8 --ignore=Z --exclude=urls.py,tests.py,*/migrations/ publicdb
	sphinx-build -anW doc doc/_build/html
