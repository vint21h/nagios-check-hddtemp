#!/usr/bin/env python

# -*- coding: utf-8 -*-

# nagios-check-hddtemp
# setup.py


from setuptools import setup, find_packages


VERSION = (1, 2, 3)
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
        "Topic :: System :: Monitoring",
        "Topic :: Utilities",
    ],
    extras_require={
        "test": [
            "attrs==20.2.0",
            "bandit==1.6.2",
            "black==20.8b1",
            "check-manifest==0.42",
            "contextlib2==0.6.0.post1",
            "coverage==5.3",
            "coveralls==2.1.2",
            "dodgy==0.2.1",
            "flake8==3.8.3",
            "flake8-annotations-complexity==0.0.5",
            "flake8-bugbear==20.1.4",
            "flake8-docstrings==1.5.0",
            "interrogate==1.3.1",
            "isort==5.5.2",
            "mypy==0.782",
            "pep8-naming==0.11.1",
            "pre-commit==2.7.1",
            "pre-commit-hooks==3.2.0",
            "pygments==2.7.1",
            "pylint==2.6.0",
            "pyroma==2.6",
            "pytest==6.0.2",
            "pytest-cov==2.10.1",
            "pytest-mock==3.3.1",
            "pytest-tldr==0.2.2",
            "readme_renderer==26.0",
            "removestar==1.2.2",
            "seed-isort-config==2.2.0",
            "tox==3.20.0",
            "tox-pyenv==1.1.0",
            "tox-travis==0.12",
            "twine==3.2.0",
        ],
        "test-old-python": [
            "check-manifest==0.41",
            "contextlib2==0.6.0.post1",
            "coverage==5.3",
            "coveralls==1.11.1",
            "pygments==2.5.2",
            "pytest-cov==2.10.1",
            "pytest-mock==2.0.0",
            "pytest-tldr==0.2.2",
            "pytest==4.6.9",
            "readme_renderer==26.0",
            "tox-pyenv==1.1.0",
            "tox-travis==0.12",
            "tox==3.20.0",
            "twine==1.15.0",
        ],
    },
)
