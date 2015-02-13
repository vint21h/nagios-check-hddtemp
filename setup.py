#!/usr/bin/env python
# -*- coding: utf-8 -*-

# nagios-check-hddtemp
# setup.py

from setuptools import setup, find_packages

VERSION = (0, 5, 7)
__version__ = '.'.join(map(str, VERSION))

DATA = ['README.rst', 'COPYING', ]

setup(
    name="nagios-check-hddtemp",
    version=__version__,
    packages=find_packages(),
    scripts=['check_hddtemp.py', ],
    package_data={
        'nagios-check-hddtemp': DATA,
    },
    data_files=[
        ('share/doc/nagios-check-hddtemp/', DATA),
    ],
    author="Alexei Andrushievich",
    author_email="vint21h@vint21h.pp.ua",
    description="Check HDD temperature Nagios plugin",
    long_description=open('README.rst').read(),
    license="GPLv3 or later",
    url="https://github.com/vint21h/nagios-check-hddtemp",
    download_url="https://github.com/vint21h/nagios-check-hddtemp/archive/%s.tar.gz" % __version__,
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        "Environment :: Console",
        "Environment :: Plugins",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: Unix",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: System :: Monitoring",
        "Topic :: Utilities",
    ]
)
