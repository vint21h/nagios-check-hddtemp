#!/usr/bin/env python
# -*- coding: utf-8 -*-

# check_hddtemp
# setup.py

import os
import warnings
from setuptools import setup, find_packages

from check_hddtemp import (
    __author__,
    __email__,
    __version__,
    __licence__,
    __description__,
    __url__,
)

SHARE_FILES = ['README.rst', 'COPYING', ]

setup(
    name = "check_hddtemp",
    version = __version__,
    packages = find_packages(),
    scripts = ['check_hddtemp.py', ],
    install_requires = ['docutils', ],
    package_data = {
        '': SHARE_FILES,
    },
    data_files = [
            ('/usr/share/doc/check_hddtemp/', SHARE_FILES),
    ],
    author = __author__,
    author_email = __email__,
    description = __description__,
    long_description = __description__,
    license = __licence__,
    url = __url__,
    zip_safe = False,
    include_package_data = True,
)
