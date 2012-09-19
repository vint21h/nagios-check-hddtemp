.. nagios-check-hddtemp
.. README.rst

A check_hddtemp documentation
=============================

    *check_hddtemp is a Nagios-plugin that that uses hddtemp (www.guzu.net/linux/hddtemp.php) to check disk temperature over the network*

.. contents::

Installation
------------
* Obtain your copy of source code from git repository: ``git clone https://github.com/vint21h/nagios-check-hddtemp.git``. Or download latest release from https://github.com/vint21h/nagios-check-hddtemp/downloads.
* Run ``./setup.py install`` from repository source tree or unpacked archive under root user.

Configuration
-------------
* Read and understand Nagios documentation.
* Add Nagios variable ``$CH$=/usr/bin/check_hddtemp.py``
* Create Nagios command and service definitions like this:

::

    # 'check_hddtemp' command
        define command
        {
            command_name check_hddtemp
            command_line $CH$ -s $ARG1$ -p $ARG2$ -d $ARG3$ -w $ARG4$ -c $ARG4$
        }

    # 'example' service
    define service
    {
        use                 local-service
        host_name           localhost
        service_description HDD Temperature /dev/sda
        check_command       check_hddtemp!127.0.0.1!7634!/dev/sda!40!50
    }

Contacts
--------
**Project Website**: https://github.com/vint21h/nagios-check-hddtemp

**Author**: Alexei Andrushievich <vint21h@vint21h.pp.ua>
