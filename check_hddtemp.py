#!/usr/bin/env python

# -*- coding: utf-8 -*-

# nagios-check-hddtemp
# check_hddtemp.py

# Copyright (c) 2011-2012 Alexei Andrushievich <vint21h@vint21h.pp.ua>
# Check HDD temperature Nagios plugin [https://github.com/vint21h/nagios-check-hddtemp]
#
# This file is part of nagios-check-hddtemp.
#
# nagios-check-hddtemp is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import sys

try:
    import socket
    import telnetlib
    from optparse import OptionParser
except ImportError, err:
    sys.stderr.write("ERROR: Couldn't load module. %s\n" % err)
    sys.exit(-1)

# metadata
__author__ = "Alexei Andrushievich"
__email__ = "vint21h@vint21h.pp.ua"
__licence__ = "GPLv3 or later"
__description__ = "Check HDD temperature Nagios plugin"
__url__ = "https://github.com/vint21h/nagios-check-hddtemp"
VERSION = (0, 4, )
__version__ = '.'.join(map(str, VERSION))


def parse_cmd_line():
    """
    Commandline options arguments parsing.
    """

    version = "%%prog %s" % __version__
    parser = OptionParser(version=version)
    parser.add_option(
        "-s", "--server", action="store", dest="server",
        type="string", default="", metavar="SERVER",
        help="server name or address"
    )
    parser.add_option(
        "-p", "--port", action="store", type="int", dest="port",
        default=7634, metavar="PORT", help="port number"
    )
    parser.add_option(
        "-d", "--device", action="store", dest="device", type="string", default="",
        metavar="DEVICE", help="device name"
    )
    parser.add_option(
        "-S", "--separator", action="store", type="string", dest="separator", default="|",
        metavar="SEPARATOR", help="hddtemp separator"
    )
    parser.add_option(
        "-w", "--warning", action="store", type="int", dest="warning",
        default=40, metavar="TEMP", help="warning temperature"
    )
    parser.add_option(
        "-c", "--critical", action="store", type="int", dest="critical",
        default=65, metavar="TEMP", help="critical temperature"
    )
    parser.add_option(
        "-t", "--timeout", action="store", type="int", dest="timeout", default=1, metavar="TIMEOUT",
        help="receiving data from hddtemp network operation timeout"
    )
    parser.add_option(
        "-q", "--quiet", metavar="QUIET", action="store_false", default=False, dest="quiet", help="be quiet"
    )

    options = parser.parse_args(sys.argv)[0]

    # check mandatory command line options supplied
    mandatories = ["server", "device", ]
    if not all(options.__dict__[mandatory] for mandatory in mandatories):
        sys.stderr.write("Mandatory command line option missing.\n")
        exit(0)

    return options


def get_hddtemp_data(server, port, timeout):
    """
    Get and return data from hddtemp server response.
    """

    response = str()

    try:
        tn = telnetlib.Telnet(server, port, timeout)
        response = tn.read_all()
        tn.close()
    except (EOFError, socket.error), err:
        sys.stderr.write("ERROR: Server communicating problem. %s\n" % err)
        sys.exit(-1)

    return response


def parse_response(response, device, separator):
    """
    Search for device and get HDD info from server response.
    """

    hdd_info_keys = ['hdd_model', 'temperature', 'scale', ]
    dev_info = {}

    response = response.split(separator * 2)
    if response:
        for dev in response:
            dev = dev.strip(separator).split(separator)
            if len(dev) != 4:
                sys.stderr.write("ERROR: Server response for device %s parsing error.\n" % device)
                sys.exit(-1)
            dev_info.update({dev[0]: dict(zip(hdd_info_keys, dev[1:]))})

        if device not in dev_info.keys():
            sys.stderr.write("ERROR: Info about device %s not found in server response.\n" % device)
            sys.exit(0)
    else:
        sys.stderr.write("ERROR: Server response too short.\n")
        sys.exit(-1)

    return dev_info[device]


def check_hddtemp(response, options):
    """
    Return info about HDD status to Nagios.
    """

    output_templates = {
        'critical': "CRITICAL: device temperature %(temperature)s%(scale)s exceeds critical temperature threshold %(critical)d%(scale)s\n",
        'warning': "WARNING: device temperature %(temperature)s%(scale)s exceeds warning temperature threshold %(warning)d%(scale)s\n",
        'ok': "OK: device is functional and stable %(temperature)s%(scale)s\n",
    }

    temperature = int(response["temperature"])

    if temperature > options.critical:
        data = {
            'temperature': temperature,
            'critical': options.critical,
            'scale': response["scale"],
        }
        template = 'critical'
    elif all([temperature > options.warning, temperature < options.critical, ]):
        data = {
            'temperature': response["temperature"],
            'warning': options.warning,
            'scale': response["scale"],
        }
        template = 'warning'
    else:
        data = {
            'temperature': response["temperature"],
            'scale': response["scale"],
        }
        template = 'ok'

    sys.stdout.write(output_templates[template] % data)

if __name__ == "__main__":
    options = parse_cmd_line()
    check_hddtemp(parse_response(get_hddtemp_data(options.server, options.port, options.timeout), options.device, options.separator), options)
    sys.exit()
