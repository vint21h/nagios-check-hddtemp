#!/usr/bin/env python

# -*- coding: utf-8 -*-

# nagios-check-hddtemp
# setup.py


from setuptools import setup, find_packages


VERSION = (1, 4, 6)
__version__ = ".".join(map(str, VERSION))

DATA = [
    "README.rst",
    "COPYING",
    "AUTHORS",
]

setup(
    name="nagios-check-hddtemp",
    version=__version__,
    packages=find_packages(exclude=["tests.*", "tests"]),
    scripts=["check_hddtemp.py"],
    package_data={"nagios-check-hddtemp": DATA},
    data_files=[("share/doc/nagios-check-hddtemp/", DATA)],
    author="Alexei Andrushievich",
    author_email="vint21h@vint21h.pp.ua",
    description="Check HDD temperature Nagios plugin",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    license="GPLv3+",
    license_file="COPYING",
    url="https://github.com/vint21h/nagios-check-hddtemp/",
    download_url="https://github.com/vint21h/nagios-check-hddtemp/archive/{version}.tar.gz".format(  # noqa: E501
        version=__version__
    ),
    zip_safe=False,
    include_package_data=True,
    python_requires=">=2.7",
    test_suite="tests",
    keywords=["nagios", "hddtemp", "check-hddtemp", "plugin", "check-hddtemp-plugin"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: Plugins",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: Unix",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: System :: Monitoring",
        "Topic :: Utilities",
    ],
    extras_require={
        "test": [
            "attrs==20.3.0",
            "bandit==1.7.0",
            "black==20.8b1",
            "check-manifest==0.46",
            "check-wheel-contents==0.2.0",
            "contextlib2==0.6.0.post1",
            "coverage==5.4",
            "coveralls==3.0.0",
            "darglint==1.6.0",
            "dodgy==0.2.1",
            "flake8-annotations-complexity==0.0.6",
            "flake8-annotations-coverage==0.0.5",
            "flake8-bugbear==20.11.1",
            "flake8-docstrings==1.5.0",
            "flake8-fixme==1.1.1",
            "flake8==3.8.4",
            "interrogate==1.3.2",
            "isort==5.7.0",
            "mypy==0.800",
            "pep8-naming==0.11.1",
            "pre-commit-hooks==3.4.0",
            "pre-commit==2.10.1",
            "pygments==2.7.4",
            "pylint==2.6.0",
            "pyroma==2.6",
            "pytest-cov==2.11.1",
            "pytest-mock==3.5.1",
            "pytest==6.2.2",
            "readme_renderer==28.0",
            "removestar==1.2.2",
            "seed-isort-config==2.2.0",
            "tabulate==0.8.7",
            "tox-gh-actions==2.4.0",
            "tox-pyenv==1.1.0",
            "tox==3.21.4",
            "twine==3.3.0",
        ],
        "test-old-python": [
            "check-manifest==0.41",
            "contextlib2==0.6.0.post1",
            "coverage==5.4",
            "coveralls==1.11.1",
            "pygments==2.5.2",
            "pytest-cov==2.11.1",
            "pytest-mock==2.0.0",
            "pytest==4.6.9",
            "readme_renderer==28.0",
            "tox-pyenv==1.1.0",
            "tox-gh-actions==2.4.0",
            "tox==3.21.4",
            "twine==1.15.0",
        ],
    },
)
