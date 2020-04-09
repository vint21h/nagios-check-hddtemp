# nagios-check-hddtemp
# Makefile


.ONESHELL:
PHONY: pipenv-install tox test bumpversion build sign check check-build check-upload upload clean coveralls release help
TEST_PYPI_URL=https://test.pypi.org/legacy/
EXTENSIONS=py,html,txt,xml
TRASH_DIRS=build dist *.egg-info .tox .mypy_cache __pycache__ htmlcov .pytest_cache
TRASH_FILES=.coverage Pipfile.lock
BUILD_TYPES=bdist_wheel sdist
VERSION=`python -c "import check_hddtemp; print(check_hddtemp.__version__);"`


pipenv-install:
	pipenv install;\
	pipenv install --dev;\


tox:
	tox;\


test:
	py.test -p no:cacheprovider -v tests --cov=check_hddtemp --verbose --color=yes;\


bumpversion:
	git tag -a $(VERSION) -m "v$(VERSION)";\


build:
	python setup.py $(BUILD_TYPES);\


sign:
	for package in `ls dist`; do\
		gpg -a --detach-sign dist/$${package};\
	done;\


check:
	pre-commit run --all-files;\


check-build:
	twine check dist/*;\


check-upload:
	twine upload --skip-existing -s --repository-url $(TEST_PYPI_URL) dist/*;\


upload:
	twine upload --skip-existing -s dist/*;\


clean:
	for file in $(TRASH_FILES); do\
		find -iname $${file} -print0 | xargs -0 rm -rf;\
	done;\
	for dir in $(TRASH_DIRS); do\
		find -type d -name $${dir} -print0 | xargs -0 rm -rf;\
	done;\


coveralls:
	coveralls;\


release:
	make bumpversion &&\
	git co master &&\
	git merge dev &&\
	git co dev &&\
	git push --all &&\
	git push --tags &&\
	make build &&\
	make sign &&\
	make check-build &&\
	make check-upload &&\
	make upload &&\
	make clean;\


help:
	@echo "    help:"
	@echo "        Show this help."
	@echo "    pipenv-install:"
	@echo "        Install all requirements."
	@echo "    tox:"
	@echo "        Run tox."
	@echo "    test:"
	@echo "        Run tests, can specify tests with 'TESTS' variable."
	@echo "    bumpversion:"
	@echo "        Tag current code revision with version."
	@echo "    build:"
	@echo "        Build python packages, can specify packages types with 'BUILD_TYPES' variable."
	@echo "    sign:"
	@echo "        Sign python packages."
	@echo "    check:"
	@echo "        Perform some code checks."
	@echo "    check-build:"
	@echo "        Run twine checks."
	@echo "    check-upload:"
	@echo "        Upload package to test PyPi using twine."
	@echo "    upload:"
	@echo "        Upload package to PyPi using twine."
	@echo "    clean:"
	@echo "        Recursively delete useless autogenerated files and directories, directories and files lists can be overriden through 'TRASH_DIRS' and 'TRASH_FILES' variables."
	@echo "    coveralls:"
	@echo "        Upload coverage report to Coveralls."
	@echo "    release:"
	@echo "        Release code."
