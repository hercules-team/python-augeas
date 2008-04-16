
all: augeas_wrap.c

clean:
	rm -f augeas.py augeas_wrap.c
	rm -fr build

augeas_wrap.c: augeas.i
	swig -python   -I/usr/include/ augeas.i

_augeas.so: augeas_wrap.c
	python setup.py build_ext

install: _augeas.so
	python setup.py install
