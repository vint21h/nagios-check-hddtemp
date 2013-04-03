#!/usr/bin/env python
# -*- coding: utf-8 -*-

# nagios-check-hddtemp
# setup.py

from setuptools import setup, find_packages

from check_hddtemp import __author__, __email__, __version__, __licence__, __description__, __url__

SHARED_FILES = ['README.rst', 'COPYING', ]

setup(
    name="nagios_check_hddtemp",
    version=__version__,
    packages=find_packages(),
    scripts=['check_hddtemp.py', ],
    package_data={
        '': SHARED_FILES,
    },
    data_files=[
        ('/usr/share/doc/nagios-check-hddtemp/', SHARED_FILES),
    ],
    author=__author__,
    author_email=__email__,
    description=__description__,
    long_description=open('README.rst').read(),
    license=__licence__,
    url=__url__,
    zip_safe=False,
    include_package_data=True
)
