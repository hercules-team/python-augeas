#!/usr/bin/env python

"""
setup.py file for augeas
"""

import os

from setuptools import setup, find_packages

prefix = os.environ.get("prefix", "/usr")


setup (name = 'python-augeas',
       version = '1.0.1',
       author      = "Harald Hoyer",
       author_email = "augeas-devel@redhat.com",
       description = """Python bindings for Augeas""",
       packages=find_packages(exclude=('test')),
       setup_requires=["cffi>=1.0.0"],
       cffi_modules=["augeas/ffi.py:ffi"],
       install_requires=["cffi>=1.0.0"],
       url = "http://augeas.net/",
       )
