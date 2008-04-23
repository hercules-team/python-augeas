
VERSION=$(shell grep version setup.py|sed -e "s/^[^']*//;s/[',]//g;")

all: build

clean:
	python setup.py clean

build:
	python setup.py build

install:
	python setup.py install

sdist:
	python setup.py sdist

srpm: sdist
	rpmbuild -ts --define "_srcrpmdir ."  dist/python-augeas-$(VERSION).tar.gz

.PHONY: sdist install build clean srpm
