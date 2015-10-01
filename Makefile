FLAKE=flake8 --max-line-length=120 --exclude=./tests
PACKAGE=bandwidth_sdk

default: clean req test pep

pep:
	$(FLAKE) $(PACKAGE) tests

test:
	tox

local_test:
	green tests -vvv -r

clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -f `find . -type f -name '@*' `
	rm -f `find . -type f -name '#*#' `
	rm -f `find . -type f -name '*.orig' `
	rm -f `find . -type f -name '*.rej' `

req:
	pip install -r requirements.txt

html_docs:
	cd docs && make html
