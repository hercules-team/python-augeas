#!/usr/bin/env python

"""
setup.py file for augeas
"""

import os
prefix = os.environ.get("prefix", "/usr")

from setuptools import setup

setup (name = 'python-augeas',
       version = '0.5.0',
       author      = "Harald Hoyer",
       author_email = "augeas-devel@redhat.com",
       description = """Python bindings for Augeas""",
       py_modules = [ "augeas", "ffi" ],
       setup_requires=["cffi>=1.0.0"],
       cffi_modules=["ffi.py:ffi"],
       install_requires=["cffi>=1.0.0"],
       url = "http://augeas.net/",
       )
