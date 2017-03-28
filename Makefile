PREFIX := /usr

VERSION = $(shell grep version setup.py|sed -e "s/^[^']*//;s/[',]//g;")

all: build

clean:
	PREFIX=$(PREFIX) python setup.py clean
	rm -f augeas.py*

distclean: clean
	rm -fr build dist MANIFEST

build:
	PREFIX=$(PREFIX) python setup.py build

install:
	PREFIX=$(PREFIX) python setup.py install

sdist:
	PREFIX=$(PREFIX) python setup.py sdist

check:
	make -C test check

srpm: sdist
	cp python-augeas.spec dist
	rpmbuild -bs --define "_srcrpmdir ."  --define '_sourcedir dist' dist/python-augeas.spec

.PHONY: sdist install build clean check distclean srpm
