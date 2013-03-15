#!/usr/bin/env python

"""
setup.py file for augeas
"""

import os

from distutils.core import setup

setup(
    name='python-augeas',
    version='0.4.1',
    author="Harald Hoyer",
    author_email="augeas-devel@redhat.com",
    description="""Python bindings for Augeas""",
    py_modules=[ "augeas" ],
    url="https://github.com/hercules-team/python-augeas",
    classifiers='''
    Programming Language :: Python :: 2
    Programming Language :: Python :: 3
    License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)
    Operating System :: POSIX :: Linux
    Intended Audience :: System Administrators
    '''.strip().splitlines(),
)
