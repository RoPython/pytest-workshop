#!/usr/bin/env python
from __future__ import absolute_import

from glob import glob
from os.path import basename, splitext

from setuptools import find_packages, setup

setup(
    name='mysite',
    version='1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    install_requires=['Django~=1.11'],
)
