VERSION = $(shell grep version setup.py|sed -e "s/^[^']*//;s/[',]//g;")

all: build

clean:
	python setup.py clean
	rm -f augeas.py* 

distclean: clean
	rm -fr build dist MANIFEST

build: augeas.py

install:
	python setup.py install

sdist:
	python setup.py sdist

upload: distcheck
	python setup.py sdist upload

distcheck:
	tox

check:
	make -C test check

srpm: sdist
	cp python-augeas.spec dist
	rpmbuild -bs --define "_srcrpmdir ."  --define '_sourcedir dist' dist/python-augeas.spec

.PHONY: sdist install build clean check distclean srpm all upload distcheck
