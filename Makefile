FLAKE=pyflakes
PEP=pep8
PACKAGE=bandwith_sdk

pep:
	$(FLAKE) $(PACKAGE) tests
	$(PEP) $(PACKAGE) tests

test:
	tox

local_test:
	green tests -vvv

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

default: req test clean pep
