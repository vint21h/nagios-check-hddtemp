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
    from string import strip
except ImportError, err:
    sys.stderr.write("ERROR: Couldn't load module. %s\n" % err)
    sys.exit(-1)

__all__ = ['parse_options', 'get_response', 'parse_response', 'check_hddtemp', 'main', ]

# metadata
__author__ = "Alexei Andrushievich"
__email__ = "vint21h@vint21h.pp.ua"
__licence__ = "GPLv3 or later"
__description__ = "Check HDD temperature Nagios plugin"
__url__ = "https://github.com/vint21h/nagios-check-hddtemp"
VERSION = (0, 4, 3)
__version__ = '.'.join(map(str, VERSION))

# global variables
OUTPUT_TEMPLATES = {
    'critical': {
        'text': "device temperature %(temperature)s%(scale)s exceeds critical temperature threshold %(critical)d%(scale)s",
        'priority': 1,
    },
    'warning': {
        'text': "device temperature %(temperature)s%(scale)s exceeds warning temperature threshold %(warning)d%(scale)s",
        'priority': 2,
    },
    'unknown': {
        'text': "device %s temperature info not found in server response",
        'priority': 3,
    },
    'ok': {
        'text': "device is functional and stable %(temperature)s%(scale)s",
        'priority': 4,
    },
}


def parse_options():
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
        "-d", "--devices", action="store", dest="devices", type="string", default="",
        metavar="DEVICES", help="comma separated devices list, or empty for all devices in hddtemp response"
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
    mandatories = ["server", ]
    if not all(options.__dict__[mandatory] for mandatory in mandatories):
        sys.stderr.write("Mandatory command line option missing.\n")
        sys.exit(0)

    return options


def get_response(options):
    """
    Get and return data from hddtemp server response.
    """

    response = str()

    try:
        tn = telnetlib.Telnet(options.server, options.port, options.timeout)
        response = tn.read_all()
        tn.close()
    except (EOFError, socket.error), err:
        sys.stderr.write("ERROR: Server communicating problem. %s\n" % err)
        sys.exit(-1)

    return response


def parse_response(response, options):
    """
    Search for device and get HDD info from server response.
    """

    hdd_info_keys = ['hdd_model', 'temperature', 'scale', ]
    devices_info = {}

    response = response.split(options.separator * 2)
    if response:
        for dev in response:
            dev = dev.strip(options.separator).split(options.separator)
            if len(dev) != 4:
                sys.stderr.write("ERROR: Server response for device %s parsing error.\n" % dev)
                sys.exit(-1)
            devices_info.update({dev[0]: dict(zip(hdd_info_keys, dev[1:]))})
    else:
        sys.stderr.write("ERROR: Server response too short.\n")
        sys.exit(-1)

    return devices_info


def check_hddtemp(response, options):
    """
    Return info about HDD status to Nagios.
    """

    devices_states = dict()

    if options.devices:
        devices = map(strip, options.devices.strip().split(','))
    else:
        devices = response.keys()

    for device in devices:
        if device:  # not empty string
            try:
                device_data = response[device]
            except KeyError:  # device not found in hddtemp response
                devices_states.update({
                    device: {
                        'template': 'unknown',
                        'temperature': None,
                        'scale': None,
                    }
                })
                continue

            # checking temperature
            temperature = int(device_data["temperature"])

            if temperature > options.critical:
                template = 'critical'
            elif all([temperature > options.warning, temperature < options.critical, ]):
                template = 'warning'
            else:
                template = 'ok'

            devices_states.update({
                device: {
                    'template': template,
                    'data': {
                        'temperature': temperature,
                        'scale': device_data["scale"],
                        'warning': options.warning,
                        'critical': options.critical,
                    }
                }
            })

    return ''
    # sys.stdout.write(OUTPUT_TEMPLATES[template] % data)


def main():
    """
    Program main.
    """

    options = parse_options()
    sys.stdout.write(check_hddtemp(parse_response(get_response(options), options), options))
    sys.exit(0)

if __name__ == "__main__":
    main()
