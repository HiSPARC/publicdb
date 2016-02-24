.PHONY: gh-pages test

gh-pages:
ifeq ($(strip $(shell git status --porcelain | wc -l)), 0)
	git checkout gh-pages
	git rm -rf .
	git clean -dxf
	git checkout HEAD .nojekyll
	git checkout master doc django_publicdb
	make -C doc/ html
	make -C doc/ latexpdf
	mv -fv doc/_build/html/* .
	mv -fv doc/_build/latex/*.pdf .
	rm -rf doc/ django_publicdb/
	git add -A
	git commit -m "Generated gh-pages for `git log master -1 --pretty=short --abbrev-commit`"
	git checkout master
else
	$(error Working tree is not clean, please commit all changes.)
endif

test:
	flake8 --ignore=Z --exclude=urls.py,tests.py,*migrations/,*raw_data/views.py django_publicdb
	flake8 --ignore=F841 django_publicdb/raw_data/views.py
