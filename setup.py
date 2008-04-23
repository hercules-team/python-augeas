#!/usr/bin/env python

"""
setup.py file for augeas
"""

import os
prefix = os.environ.get("prefix", "/usr")

from distutils.core import setup, Extension


augeas_module = Extension('_augeas',
                          sources=['augeas.i'],
                          libraries=['augeas'],                          
                          swig_opts=['-Wall', '-I'+prefix+'/include/'],
                          )

setup (name = 'python-augeas',
       version = '0.0.8',
       author      = "Harald Hoyer",
       author_email = "augeas-devel@redhat.com",
       description = """Python bindings for Augeas""",
       ext_modules = [augeas_module],
       py_modules = ["augeas"],
       url = "http://augeas.net/",
       )
