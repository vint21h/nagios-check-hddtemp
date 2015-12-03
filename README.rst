.. nagios-check-hddtemp
.. README.rst

A nagios-check-hddtemp documentation
====================================

    *nagios-check-hddtemp is a Nagios-plugin that uses hddtemp (www.guzu.net/linux/hddtemp.php) to check disk temperature over the network*

.. contents::

Installation
------------
* Obtain your copy of source code from git repository: ``git clone https://github.com/vint21h/nagios-check-hddtemp.git``. Or download latest release from https://github.com/vint21h/nagios-check-hddtemp/tags.
* Run ``python ./setup.py install`` from repository source tree or unpacked archive under root user. Or use pip: ``pip install nagios-check-hddtemp``.

Configuration
-------------
* Read and understand Nagios documentation.
* Create Nagios command and service definitions like this:

::

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

Without ``--devices`` option script check all devices from hddtemp response and return priority based global status:

* critical
* warning
* unknown
* ok

Also, ``--devices`` option can take comma separated list of devices to check.

If you want receive devices performance data, add ``-P`` argument to ``command_line``.

Licensing
---------
nagios-check-hddtemp is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
For complete license text see COPYING file.

Contacts
--------
**Project website**: https://github.com/vint21h/nagios-check-hddtemp

**Author**: Alexei Andrushievich <vint21h@vint21h.pp.ua>

For other authors list see AUTHORS file.
