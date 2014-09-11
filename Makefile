TEST_DIR=$(CURDIR)/test
RESOURCES_DIR=$(CURDIR)/resources

################################################################################


upload: test register
	python setup.py sdist upload

register:
	python setup.py register

################################################################################


test: check
	RESOURCES_DIR=$(RESOURCES_DIR) python -m unittest discover -p '*_test.py'

reinstall: uninstall install

install:check
	python setup.py install

uninstall:
	pip uninstall --yes proso-model

check:
	pep8 --ignore=E501,E225,E123 proso
	pyflakes proso

