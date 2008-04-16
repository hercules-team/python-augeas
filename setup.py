#!/usr/bin/env python

"""
setup.py file for augeas
"""

from distutils.core import setup, Extension


augeas_module = Extension('_augeas',
                          sources=['augeas_wrap.c'],
                          libraries=['augeas'],                          
                          )

setup (name = 'augeas',
       version = '0.1',
       author      = "Author",
       description = """Augeas""",
       ext_modules = [augeas_module],
       py_modules = ["augeas"],
       )
