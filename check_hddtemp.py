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
import socket
import telnetlib
from argparse import ArgumentParser
from collections import OrderedDict


__all__ = [
    "CheckHDDTemp",
    "main",
]


# metadata
VERSION = (1, 4, 1)
__version__ = ".".join(map(str, VERSION))


class CheckHDDTemp(object):
    """
    Check HDD temperature Nagios plugin.
    """

    HDDTEMP_SLEEPING = "SLP"
    HDDTEMP_UNKNOWN = "UNK"
    STATUS_CRITICAL, STATUS_WARNING, STATUS_UNKNOWN, STATUS_OK, STATUS_SLEEPING = [
        "critical",
        "warning",
        "unknown",
        "ok",
        "sleeping",
    ]
    (
        PRIORITY_CRITICAL,
        PRIORITY_WARNING,
        PRIORITY_UNKNOWN,
        PRIORITY_OK,
        PRIORITY_SLEEPING,
    ) = range(1, 6)
    PRIORITY_TO_STATUS = {
        PRIORITY_CRITICAL: STATUS_CRITICAL,
        PRIORITY_WARNING: STATUS_WARNING,
        PRIORITY_UNKNOWN: STATUS_UNKNOWN,
        PRIORITY_OK: STATUS_OK,
        PRIORITY_SLEEPING: STATUS_SLEEPING,
    }
    OUTPUT_TEMPLATES = {
        STATUS_CRITICAL: {
            "text": "device {device} temperature {temperature}{scale} exceeds critical temperature threshold {critical}{scale}",  # noqa: E501
            "priority": PRIORITY_CRITICAL,
        },
        STATUS_WARNING: {
            "text": "device {device} temperature {temperature}{scale} exceeds warning temperature threshold {warning}{scale}",  # noqa: E501
            "priority": PRIORITY_WARNING,
        },
        STATUS_UNKNOWN: {
            "text": "device {device} temperature info not found in server response or can't be recognized by hddtemp",  # noqa: E501
            "priority": PRIORITY_UNKNOWN,
        },
        STATUS_OK: {
            "text": "device {device} is functional and stable {temperature}{scale}",
            "priority": PRIORITY_OK,
        },
        STATUS_SLEEPING: {
            "text": "device {device} is sleeping",
            "priority": PRIORITY_SLEEPING,
        },
    }
    DEFAULT_EXIT_CODE = 3
    EXIT_CODES = {
        STATUS_OK: 0,
        STATUS_SLEEPING: 0,
        STATUS_WARNING: 1,
        STATUS_CRITICAL: 2,
        STATUS_UNKNOWN: 3,
    }
    PERFORMANCE_DATA_TEMPLATE = "{device}={temperature}"

    def __init__(self):
        """
        Get command line args.
        """

        self.options = self._get_options()  # type: ignore

    @staticmethod
    def _get_options():
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
            "-v",
            "--version",
            action="version",
            version="{version}".format(version=__version__),
        )

        options = parser.parse_args()

        # check mandatory command line options supplied
        if not options.server:
            parser.error(message="Required server address option missing")

        # check if waning temperature in args less than critical
        if options.warning >= options.critical:
            parser.error(
                message="Warning temperature option value must be less than critical option value"  # noqa: E501
            )

        return options

    def _get_data(self):
        """
        Get and return data from hddtemp server.

        :return: data from hddtemp server
        :rtype: str
        """

        try:
            connection = telnetlib.Telnet(
                self.options.server, self.options.port, self.options.timeout
            )
            response = connection.read_all()
            connection.close()

            return response.decode("utf8")

        except (EOFError, socket.error) as error:
            if not self.options.quiet:
                sys.stdout.write(
                    "ERROR: Server communication problem. {error}\n".format(error=error)
                )

            sys.exit(self.DEFAULT_EXIT_CODE)

    def _parse_data(self, data):
        """
        Search for device and get HDD info from server response.

        :param data: hddtemp server response
        :type data: str
        :return: structured data parsed from hddtemp server response
        :rtype: Dict[str, Dict[str, str]]
        """

        info = {}
        data = data.split(self.options.separator * 2)

        if data != [""]:
            for device in data:
                device = device.strip(self.options.separator).split(
                    self.options.separator
                )
                if len(device) != 4:  # 4 data items in server response for device
                    if not self.options.quiet:
                        sys.stdout.write(
                            "ERROR: Server response for device '{dev}' parsing error\n".format(  # noqa: E501
                                dev=device
                            )
                        )
                    sys.exit(self.DEFAULT_EXIT_CODE)
                dev, model, temperature, scale = device
                info.update(
                    {dev: {"model": model, "temperature": temperature, "scale": scale}}
                )
        else:
            if not self.options.quiet:
                sys.stdout.write("ERROR: Server response too short\n")
            sys.exit(self.DEFAULT_EXIT_CODE)

        return info

    def _check_data(self, data):
        """
        Create devices states info.

        :param data: structured data parsed from hddtemp server response
        :type data: Dict[str, Dict[str, str]]
        :return: devices states info
        :rtype: Dict[str, Dict[str, Union[str, int, Dict[str, Union[None, int, str]]]]]
        """

        states = {}
        devices = (
            map(lambda dev: dev.strip(), self.options.devices.strip().split(","))
            if self.options.devices
            else data.keys()
        )

        for device in devices:
            if device:  # not empty string
                try:
                    info = data[device]
                except KeyError:  # device not found in hddtemp response
                    states.update(
                        {
                            device: {
                                "template": self.STATUS_UNKNOWN,
                                "priority": self.OUTPUT_TEMPLATES[self.STATUS_UNKNOWN][
                                    "priority"
                                ],
                                "data": {
                                    "device": device,
                                    "temperature": None,
                                    "scale": None,
                                    "warning": self.options.warning,
                                    "critical": self.options.critical,
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

                if temperature == self.HDDTEMP_SLEEPING:  # type: ignore
                    template = self.STATUS_SLEEPING
                elif temperature == self.HDDTEMP_UNKNOWN:  # type: ignore
                    template = self.STATUS_UNKNOWN
                elif temperature > self.options.critical:
                    template = self.STATUS_CRITICAL
                elif all(
                    [
                        temperature > self.options.warning,
                        temperature < self.options.critical,
                    ]
                ):
                    template = self.STATUS_WARNING
                else:
                    template = self.STATUS_OK

                states.update(
                    {
                        device: {
                            "template": template,
                            "priority": self.OUTPUT_TEMPLATES[template]["priority"],
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

    def _get_status(self, data):
        """
        Create main status.

        :param data: devices states info
        :type data: Dict[str, Dict[str, Union[str, int, Dict[str, Union[None, int, str]]]]]  # noqa: E501
        :return: main check status
        :rtype: str
        """

        # for multiple check need to get main status by priority
        priority = min([info["priority"] for device, info in data.items()])
        status = self.PRIORITY_TO_STATUS.get(priority, self.PRIORITY_CRITICAL)

        return status

    def _get_code(self, status):
        """
        Create exit code.

        :param status: main check status
        :type status: str
        :return: exit code
        :rtype: int
        """

        return self.EXIT_CODES.get(status, self.DEFAULT_EXIT_CODE)

    def _get_output(self, data, status):
        """
        Create human readable HDD's statuses.

        :param data: devices states info
        :type data: Dict[str, Dict[str, Union[str, int, Dict[str, Union[None, int, str]]]]]  # noqa: E501
        :param status: main check status
        :type status: str
        :return: human readable HDD's statuses
        :rtype: str
        """

        output = ""
        # sort devices data by priority
        data = OrderedDict(
            sorted(data.items(), key=lambda item: (item[1]["priority"], item[0]))
        )

        # create output
        devices = ", ".join(
            [
                str(self.OUTPUT_TEMPLATES[data[device]["template"]]["text"]).format(
                    **data[device]["data"]
                )
                for device in data.keys()
            ]
        )

        # create full status string with main status for multiple devices
        # and all devices states with performance data (optional)
        output = (
            "{status}: {data} | {performance-data}\n".format(
                **{
                    "status": status.upper(),
                    "data": devices,
                    "performance-data": "; ".join(
                        [
                            self.PERFORMANCE_DATA_TEMPLATE.format(
                                **data[device]["data"]
                            )
                            for device in data.keys()
                        ]
                    ),
                }
            )
            if self.options.performance
            else "{status}: {data}\n".format(
                **{"status": status.upper(), "data": devices}
            )
        )

        return output

    def check(self):
        """
        Get data from server, parse server response, check and create plugin output.

        :return: plugin output and exit code
        :rtype: Tuple[str, int]
        """

        data = self._check_data(data=self._parse_data(data=self._get_data()))  # type: ignore  # noqa: E501
        status = self._get_status(data=data)  # type: ignore
        code = self._get_code(status=status)  # type: ignore

        return self._get_output(data=data, status=status), code  # type: ignore


def main():
    """
    Program main.
    """

    checker = CheckHDDTemp()  # type: ignore
    output, code = checker.check()  # type: ignore
    sys.stdout.write(output)
    sys.exit(code)


if __name__ == "__main__":

    main()  # type: ignore
