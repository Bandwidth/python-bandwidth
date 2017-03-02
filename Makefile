default: clean req test

test:
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
	rm -rf sphinx_docs/build
	cd sphinx_docs && make html
	cp -fR sphinx_docs/build/html/ docs/

pep:
	find ./bandwidth -name \*.py -exec pep8 --ignore=E402 --max-line-length 120 {} +
	find ./tests -name \*.py -exec pep8 --ignore=E402 --max-line-length 120 {} +

auto_pep_tests:
	find ./tests -name \*.py -exec autopep8 --recursive --aggressive --aggressive --in-place --max-line-length 120 {} +

auto_pep_source:
	find ./bandwidth -name \*.py -exec autopep8 --recursive --aggressive --aggressive --in-place --max-line-length 120 {} +

auto_pep: pep auto_pep_source auto_pep_tests
