#!/usr/bin/env python

# -*- coding: utf-8 -*-

# nagios-check-hddtemp
# check_hddtemp.py

# Copyright (c) 2011-2020 Alexei Andrushievich <vint21h@vint21h.pp.ua>
# Check HDD temperature Nagios plugin [https://github.com/vint21h/nagios-check-hddtemp/]
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
    from argparse import ArgumentParser
    import socket
    import telnetlib
except ImportError as error:
    sys.stderr.write("ERROR: Couldn't load module. {error}\n".format(error=error))
    sys.exit(-1)


__all__ = [
    "CheckHDDTemp",
    "main",
]


# metadata
VERSION = (0, 9, 0)
__version__ = ".".join(map(str, VERSION))


class CheckHDDTemp(object):
    """
    Check HDD temperature Nagios plugin.
    """

    OUTPUT_TEMPLATES = {
        "critical": {
            "text": "device {device} temperature {temperature}{scale} exceeds critical temperature threshold {critical}{scale}",  # noqa: E501
            "priority": 1,
        },
        "warning": {
            "text": "device {device} temperature {temperature}{scale} exceeds warning temperature threshold {warning}{scale}",  # noqa: E501
            "priority": 2,
        },
        "unknown": {
            "text": "device {device} temperature info not found in server response or can't be recognized by hddtemp",  # noqa: E501
            "priority": 3,
        },
        "ok": {
            "text": "device {device} is functional and stable {temperature}{scale}",
            "priority": 4,
        },
        "sleeping": {"text": "device {device} is sleeping", "priority": 5},
    }
    EXIT_CODES = {
        "ok": 0,
        "sleeping": 0,
        "warning": 1,
        "critical": 2,
    }
    PERFORMANCE_DATA_TEMPLATE = "{device}={temperature}"

    def __init__(self):
        """
        Get command line args.
        """

        self.options = self.get_options()

    @staticmethod
    def get_options():
        """
        Parse commandline options arguments.

        :return: parsed command line arguments
        :rtype: Namespace
        """

        parser = ArgumentParser(description="Check HDD temperature Nagios plugin")
        parser.add_argument(
            "-s",
            "--server",
            action="store",
            dest="server",
            type=str,
            default="",
            metavar="SERVER",
            help="server name or address",
        )
        parser.add_argument(
            "-p",
            "--port",
            action="store",
            type=int,
            dest="port",
            default=7634,
            metavar="PORT",
            help="port number",
        )
        parser.add_argument(
            "-d",
            "--devices",
            action="store",
            dest="devices",
            type=str,
            default="",
            metavar="DEVICES",
            help="comma separated devices list, or empty for all devices in hddtemp response",  # noqa: E501
        )
        parser.add_argument(
            "-S",
            "--separator",
            action="store",
            type=str,
            dest="separator",
            default="|",
            metavar="SEPARATOR",
            help="hddtemp separator",
        )
        parser.add_argument(
            "-w",
            "--warning",
            action="store",
            type=int,
            dest="warning",
            default=40,
            metavar="TEMPERATURE",
            help="warning temperature",
        )
        parser.add_argument(
            "-c",
            "--critical",
            action="store",
            type=int,
            dest="critical",
            default=65,
            metavar="TEMPERATURE",
            help="critical temperature",
        )
        parser.add_argument(
            "-t",
            "--timeout",
            action="store",
            type=int,
            dest="timeout",
            default=1,
            metavar="TIMEOUT",
            help="receiving data from hddtemp operation network timeout",
        )
        parser.add_argument(
            "-P",
            "--performance-data",
            action="store_true",
            default=False,
            dest="performance",
            help="return performance data",
        )
        parser.add_argument(
            "-q",
            "--quiet",
            action="store_true",
            default=False,
            dest="quiet",
            help="be quiet",
        )
        parser.add_argument(
            "--version",
            action="version",
            version="{version}".format(**{"version": __version__}),
        )

        options = parser.parse_args()

        # check mandatory command line options supplied
        if not options.server:
            parser.error("Required server address option missing")

        # check if waning temperature in args less than critical
        if options.warning >= options.critical:
            parser.error(
                "Warning temperature option value must be less than critical option value"  # noqa: E501
            )

        return options

    def get_data(self):
        """
        Get and return data from hddtemp server.

        :return: data from hddtemp server
        :rtype: str
        """

        try:
            tn = telnetlib.Telnet(
                self.options.server, self.options.port, self.options.timeout
            )
            response = tn.read_all()
            tn.close()

            return response.decode("utf8")

        except (EOFError, socket.error) as error:
            if not self.options.quiet:
                sys.stdout.write(
                    "ERROR: Server communication problem. {error}\n".format(error=error)
                )

            sys.exit(3)

    def parse_response(self, response):
        """
        Search for device and get HDD info from server response.

        :param response: hddtemp server response
        :type response: str
        :return: structured data parsed from hddtemp server response
        :rtype: Dict[str, Dict[str, str]]
        """

        data = {}
        response = response.split(self.options.separator * 2)

        if response:
            for info in response:
                info = info.strip(self.options.separator).split(self.options.separator)
                if len(info) != 4:
                    if not self.options.quiet:
                        sys.stdout.write(
                            "ERROR: Server response for device '{dev}' parsing error\n".format(  # noqa: E501
                                dev=info
                            )
                        )
                    sys.exit(3)
                dev, model, temperature, scale = info
                data.update(
                    {dev: {"model": model, "temperature": temperature, "scale": scale}}
                )
        else:
            if not self.options.quiet:
                sys.stdout.write("ERROR: Server response too short\n")
            sys.exit(3)

        return data

    def check_hddtemp(self, data):
        """
        Create devices states info.

        :param data: structured data parsed from hddtemp server response
        :type data: Dict[str, Dict[str, str]]
        :return: devices states info
        :rtype: Dict[str, Dict[str, Union[str, Dict[str, Union[None, int, str]]]]]
        """

        states = dict()

        if self.options.devices:
            devices = map(
                lambda dev: dev.strip(), self.options.devices.strip().split(",")
            )
        else:
            devices = data.keys()

        for device in devices:
            if device:  # not empty string
                try:
                    info = data[device]
                except KeyError:  # device not found in hddtemp response
                    states.update(
                        {
                            device: {
                                "template": "unknown",
                                "data": {
                                    "device": device,
                                    "temperature": None,
                                    "scale": None,
                                    "warning": None,
                                    "critical": None,
                                },
                            }
                        }
                    )
                    continue

                # checking temperature
                # sometime getting "SLP" or "UNK" instead of temperature
                try:
                    temperature = int(info["temperature"])
                except ValueError:
                    temperature = info["temperature"]

                if temperature == "SLP":
                    template = "sleeping"
                elif temperature == "UNK":
                    template = "unknown"
                elif temperature > self.options.critical:
                    template = "critical"
                elif all(
                    [
                        temperature > self.options.warning,
                        temperature < self.options.critical,
                    ]
                ):
                    template = "warning"
                else:
                    template = "ok"

                states.update(
                    {
                        device: {
                            "template": template,
                            "data": {
                                "device": device,
                                "temperature": temperature,
                                "scale": info["scale"],
                                "warning": self.options.warning,
                                "critical": self.options.critical,
                            },
                        }
                    }
                )

        return states

    def output(self, states):
        """
        Create Nagios and human readable HDD's statuses.

        :param states: devices states info
        :type states: Dict[str, Dict[str, Union[str, Dict[str, Union[None, int, str]]]]]
        :return: Nagios and human readable HDD's statuses
        :rtype: Tuple[str, int]
        """

        output = ""

        # getting main status for check
        # (for multiple check need to get main status by priority)
        status = [
            status[0]
            for status in sorted(
                [
                    (status, self.OUTPUT_TEMPLATES[status]["priority"])
                    for status in list(
                        set([states[data]["template"] for data in states.keys()])
                    )
                ],
                key=lambda x: x[1],
            )
        ][0]
        code = self.EXIT_CODES.get(status, 3)  # create exit code
        devices = ", ".join(
            [
                self.OUTPUT_TEMPLATES[states[data]["template"]]["text"].format(
                    **states[data]["data"]
                )
                for data in states.keys()
            ]
        )

        # create full status string with main status for multiple devices
        # and all devices states with performance data (optional)
        if self.options.performance:
            output = "{status}: {data} | {performance-data}\n".format(
                **{
                    "status": status.upper(),
                    "data": devices,
                    "performance-data": "; ".join(
                        [
                            self.PERFORMANCE_DATA_TEMPLATE.format(**states[d]["data"])
                            for d in states.keys()
                        ]
                    ),
                }
            )
        else:
            output = "{status}: {data}\n".format(
                **{"status": status.upper(), "data": devices}
            )

        return output, code

    def check(self):
        """
        Get data from server, parse server response, check and create plugin output.

        :return: nothing
        :rtype: None
        """

        return self.output(
            states=self.check_hddtemp(
                data=self.parse_response(response=self.get_data())
            )
        )


def main():
    """
    Program main.
    """

    checker = CheckHDDTemp()
    output, code = checker.check()
    sys.stdout.write(output)
    sys.exit(code)


if __name__ == "__main__":

    main()
