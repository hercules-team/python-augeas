#!/usr/bin/env python

"""
setup.py file for augeas
"""

from distutils.core import setup, Extension


augeas_module = Extension('_augeas',
                          sources=['augeas_wrap.c'],
                          libraries=['augeas'],                          
                          )

setup (name = 'python-augeas',
       version = '0.0.8',
       author      = "Harald Hoyer",
       author_email = "augeas-devel@redhat.com",
       description = """Python bindings for Augeas""",
       ext_modules = [augeas_module],
       py_modules = ["augeas"],
       url = "http://augeas.net/"
       )
