PREFIX=/usr

all: augeas_wrap.c

clean:
	rm -f augeas.py augeas_wrap.c
	rm -fr build

augeas_wrap.c: augeas.i
	swig -python   -I$(PREFIX)/include/ augeas.i

_augeas.so: augeas_wrap.c
	python setup.py build_ext

install: _augeas.so
	python setup.py install

sdist: augeas_wrap.c
	python setup.py sdist

.PHONY: sdist
