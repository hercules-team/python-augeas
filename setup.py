#!/usr/bin/env python

"""
setup.py file for augeas
"""

import os

from setuptools import setup, find_packages

prefix = os.environ.get("prefix", "/usr")


setup (name = 'python-augeas',
       version = '1.0.3',
       author      = "Harald Hoyer",
       author_email = "augeas-devel@redhat.com",
       description = """Python bindings for Augeas""",
       packages=find_packages(exclude=('test')),
       setup_requires=["cffi>=1.0.0"],
       cffi_modules=["augeas/ffi.py:ffi"],
       install_requires=["cffi>=1.0.0"],
       url = "http://augeas.net/",
       classifiers=[
           "Programming Language :: Python :: 2.7",
           "Programming Language :: Python :: 3.4",
           "Programming Language :: Python :: 3.5",
           "Programming Language :: Python :: 3.6",
           "Programming Language :: Python :: Implementation :: CPython",
           "Programming Language :: Python :: Implementation :: PyPy",
       ],
       )
