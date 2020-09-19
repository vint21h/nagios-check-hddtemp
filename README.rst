.. nagios-check-hddtemp
.. README.rst

A nagios-check-hddtemp documentation
====================================

|Travis|_ |Coveralls|_ |pypi-license|_ |pypi-version|_ |pypi-python-version|_ |pypi-format|_ |pypi-wheel|_ |pypi-status|_

    *nagios-check-hddtemp is a Nagios-plugin that uses hddtemp (www.guzu.net/linux/hddtemp.php) to check disk temperature over the network*

.. contents::

Installation
------------
* Obtain your copy of source code from the git repository: ``$ git clone https://github.com/vint21h/nagios-check-hddtemp.git``. Or download the latest release from https://github.com/vint21h/nagios-check-hddtemp/tags/.
* Run ``$ python ./setup.py install`` from the repository source tree or unpacked archive. Or use pip: ``$ pip install nagios-check-hddtemp``.

Configuration
-------------
* Read and understand Nagios documentation.
* Create Nagios command and service definitions like this:

.. code-block::

    # "check_hddtemp" command
    define command
    {
        command_name check_hddtemp
        command_line $USER1$/check_hddtemp -s $ARG1$ -p $ARG2$ -d $ARG3$ -w $ARG4$ -c $ARG4$
    }

    # "check_hddtemp" service for /dev/sda
    define service
    {
        use                 local-service
        host_name           localhost
        service_description HDD Temperature /dev/sda
        check_command       check_hddtemp!127.0.0.1!7634!/dev/sda!40!50
    }

Without ``--devices`` option plugin checks all devices from hddtemp response and returns priority-based global status:

* critical
* warning
* unknown
* ok
* sleeping

Also, ``--devices`` option can take comma-separated list of devices to check.

If you want to receive devices performance data, add ``-P`` argument to the command line.

Licensing
---------
nagios-check-hddtemp is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
For complete license text see COPYING file.

Contacts
--------
**Project website**: https://github.com/vint21h/nagios-check-hddtemp/

**Author**: Alexei Andrushievich <vint21h@vint21h.pp.ua>

For other authors list see AUTHORS file.


.. |Travis| image:: https://travis-ci.org/vint21h/nagios-check-hddtemp.svg?branch=master
    :alt: Travis
.. |Coveralls| image:: https://coveralls.io/repos/github/vint21h/nagios-check-hddtemp/badge.svg?branch=master
    :alt: Coveralls
.. |pypi-license| image:: https://img.shields.io/pypi/l/nagios-check-hddtemp
    :alt: License
.. |pypi-version| image:: https://img.shields.io/pypi/v/nagios-check-hddtemp
    :alt: Version
.. |pypi-python-version| image:: https://img.shields.io/pypi/pyversions/nagios-check-hddtemp
    :alt: Supported Python version
.. |pypi-format| image:: https://img.shields.io/pypi/format/nagios-check-hddtemp
    :alt: Package format
.. |pypi-wheel| image:: https://img.shields.io/pypi/wheel/nagios-check-hddtemp
    :alt: Python wheel support
.. |pypi-status| image:: https://img.shields.io/pypi/status/nagios-check-hddtemp
    :alt: Package status
.. _Travis: https://travis-ci.org/vint21h/nagios-check-hddtemp/
.. _Coveralls: https://coveralls.io/github/vint21h/nagios-check-hddtemp?branch=master
.. _pypi-license: https://pypi.org/project/nagios-check-hddtemp/
.. _pypi-version: https://pypi.org/project/nagios-check-hddtemp/
.. _pypi-python-version: https://pypi.org/project/nagios-check-hddtemp/
.. _pypi-format: https://pypi.org/project/nagios-check-hddtemp/
.. _pypi-wheel: https://pypi.org/project/nagios-check-hddtemp/
.. _pypi-status: https://pypi.org/project/nagios-check-hddtemp/
