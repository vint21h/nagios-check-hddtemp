#!/usr/bin/env python

# -*- coding: utf-8 -*-

# nagios-check-hddtemp
# check_hddtemp.py

# Copyright (c) 2011-2016 Alexei Andrushievich <vint21h@vint21h.pp.ua>
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

from __future__ import unicode_literals
import sys

try:
    import socket
    import telnetlib
    from optparse import OptionParser
    from string import strip
except ImportError, error:
    sys.stderr.write("ERROR: Couldn't load module. {error}\n".format(error=error))
    sys.exit(-1)

__all__ = ["main", ]

# metadata
VERSION = (0, 8, 2)
__version__ = ".".join(map(str, VERSION))

# global variables
OUTPUT_TEMPLATES = {
    "critical": {
        "text": "device {device} temperature {temperature}{scale} exceeds critical temperature threshold {critical}{scale}",
        "priority": 1,
    },
    "warning": {
        "text": "device {device} temperature {temperature}{scale} exceeds warning temperature threshold {warning}{scale}",
        "priority": 2,
    },
    "unknown": {
        "text": "device {device} temperature info not found in server response",
        "priority": 3,
    },
    "ok": {
        "text": "device {device} is functional and stable {temperature}{scale}",
        "priority": 4,
    },
}
EXIT_CODES = {
    "ok": 0,
    "warning": 1,
    "critical": 2,
}
PERFORMANCE_DATA_TEMPLATE = "{device}={temperature}"


def parse_options():
    """
    Commandline options arguments parsing.
    """

    version = "%%prog {version}".format(version=__version__)
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
        default=40, metavar="TEMPERATURE", help="warning temperature"
    )
    parser.add_option(
        "-c", "--critical", action="store", type="int", dest="critical",
        default=65, metavar="TEMPERATURE", help="critical temperature"
    )
    parser.add_option(
        "-t", "--timeout", action="store", type="int", dest="timeout", default=1, metavar="TIMEOUT",
        help="receiving data from hddtemp operation network timeout"
    )
    parser.add_option(
        "-P", "--performance-data", action="store_true", default=False, dest="performance", help="return performance data"
    )
    parser.add_option(
        "-q", "--quiet", action="store_true", default=False, dest="quiet", help="be quiet"
    )

    options = parser.parse_args(sys.argv)[0]

    # check mandatory command line options supplied
    if not options.server:
        parser.error("Required server address option missing")

    # check if waning temperature in args less than critical
    if options.warning >= options.critical:
        parser.error("Warning temperature option value must be less then critical option value")

    return options


def get_response(options):
    """
    Get and return data from hddtemp server response.
    """

    response = ""

    try:
        tn = telnetlib.Telnet(options.server, options.port, options.timeout)
        response = tn.read_all()
        tn.close()
    except (EOFError, socket.error, ), error:
        if not options.quiet:
            sys.stdout.write("ERROR: Server communication problem. {error}\n".format(error=error))
        sys.exit(3)

    return response


def parse_response(response, options):
    """
    Search for device and get HDD info from server response.
    """

    data_keys = ["hdd_model", "temperature", "scale", ]
    data = {}

    response = response.split(options.separator * 2)
    if response:
        for dev in response:
            dev = dev.strip(options.separator).split(options.separator)
            if len(dev) != 4:
                if not options.quiet:
                    sys.stdout.write("ERROR: Server response for device '{dev}' parsing error\n".format(dev=dev))
                sys.exit(3)
            data.update({dev[0]: dict(zip(data_keys, dev[1:]))})
    else:
        if not options.quiet:
            sys.stdout.write("ERROR: Server response too short\n")
        sys.exit(3)

    return data


def check_hddtemp(data, options):
    """
    Create devices statuses info.
    """

    devices_states = dict()

    if options.devices:
        devices = map(strip, options.devices.strip().split(","))
    else:
        devices = data.keys()

    for device in devices:
        if device:  # not empty string
            try:
                device_data = data[device]
            except KeyError:  # device not found in hddtemp response
                devices_states.update({
                    device: {
                        "template": "unknown",
                        "data": {
                            "device": device,
                            "temperature": None,
                            "scale": None,
                            "warning": None,
                            "critical": None,
                        }
                    }
                })
                continue

            # checking temperature
            temperature = int(device_data["temperature"])

            if temperature > options.critical:
                template = "critical"
            elif all([temperature > options.warning, temperature < options.critical, ]):
                template = "warning"
            else:
                template = "ok"

            devices_states.update({
                device: {
                    "template": template,
                    "data": {
                        "device": device,
                        "temperature": temperature,
                        "scale": device_data["scale"],
                        "warning": options.warning,
                        "critical": options.critical,
                    }
                }
            })

    return devices_states


def create_output(data, options):
    """
    Create Nagios and human readable hdd's statuses.
    """

    output = ""

    # getting main status for check (for multiple check need to get main status by priority)
    status = [status[0] for status in sorted([(status, OUTPUT_TEMPLATES[status]["priority"]) for status in list(set([data[d]["template"] for d in data.keys()]))], key=lambda x: x[1])][0]
    code = EXIT_CODES.get(status, 3)  # create exit code
    devices = ", ".join([OUTPUT_TEMPLATES[data[d]["template"]]["text"].format(**data[d]["data"]) for d in data.keys()])

    # create full status string with main status for multiple devices and all devices states with performance data (optional)
    if options.performance:
        output = "{status}: {data} | {performance-data}\n".format(**{
            "status": status.upper(),
            "data": devices,
            "performance-data": "; ".join([PERFORMANCE_DATA_TEMPLATE.format(**data[d]["data"]) for d in data.keys()])
        })
    else:
        output = "{status}: {data}\n".format(**{
            "status": status.upper(),
            "data": devices,
        })

    return output, code


def main():
    """
    Program main.
    """

    options = parse_options()
    output, code = create_output(check_hddtemp(parse_response(get_response(options), options), options), options)
    sys.stdout.write(output)
    sys.exit(code)

if __name__ == "__main__":

    main()
