# -*- coding: utf-8 -*-

# nagios-check-hddtemp
# tests/check_hddtemp_test.py


from __future__ import unicode_literals

from argparse import Namespace
import socket

import pytest

from check_hddtemp import CheckHDDTemp


__all__ = [
    "test_get_options",
    "test_get_options__missing_server_option",
    "test_get_options__warning_gte_critical",
    "test_get_data",
    "test_get_data__network_error",
    "test_parse_response",
    "test_parse_response__parsing_error",
    "test_parse_response__too_short_error",
    "test_check_hddtemp",
    "test_check_hddtemp__critical",
    "test_check_hddtemp__sleeping_device",
    "test_check_hddtemp__unknown_device",
    "test_check_hddtemp__unknown_device_temperature",
    "test_check_hddtemp__warning",
]


def test_get_options(mocker):
    """
    Test "get_options" method must return argparse namespace.
    """

    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()

    assert isinstance(checker.options, Namespace)  # nosec: B101


def test_get_options__missing_server_option(mocker):
    """
    Test "get_options" method must exit with server option missing error.
    """

    mocker.patch("sys.argv", ["check_hddtemp.py"])
    with pytest.raises(SystemExit):
        CheckHDDTemp()


def test_get_options__warning_gte_critical(mocker):
    """
    Test "get_options" method must exit with warning option
    greater or equal than critical error.
    """

    mocker.patch("sys.argv", ["check_hddtemp.py", "-w", "65", "-c", "40"])
    with pytest.raises(SystemExit):
        CheckHDDTemp()


def test_get_data(mocker):
    """
    Test "get_options" method must return data from server.
    """

    expected = "|/dev/sda|HARD DRIVE|28|C|"
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    mocker.patch("telnetlib.Telnet.open")
    mocker.patch(
        "telnetlib.Telnet.read_all",
        lambda data: b"|/dev/sda|HARD DRIVE|28|C|",  # noqa: E501
    )
    checker = CheckHDDTemp()
    result = checker.get_data()

    assert result == expected  # nosec: B101


def test_get_data__network_error(mocker):
    """
    Test "get_options" method must exit with network error.
    """

    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    mocker.patch("telnetlib.Telnet.read_all", side_effect=socket.error)
    with pytest.raises(SystemExit):
        checker = CheckHDDTemp()
        checker.get_data()


def test_parse_response(mocker):
    """
    Test "parse_response" method must return structured data.
    """

    expected = {
        "/dev/sda": {"model": "HARD DRIVE", "temperature": "28", "scale": "C"},
    }
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()
    result = checker.parse_response(response="|/dev/sda|HARD DRIVE|28|C|")  # noqa: E501

    assert result == expected  # nosec: B101


def test_parse_response__too_short_error(mocker):
    """
    Test "parse_response" method must exit with too short response error.
    """

    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    with pytest.raises(SystemExit):
        checker = CheckHDDTemp()
        checker.parse_response(response="")


def test_parse_response__parsing_error(mocker):
    """
    Test "parse_response" method must exit with parsing error.
    """

    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    with pytest.raises(SystemExit):
        checker = CheckHDDTemp()
        checker.parse_response(response="|/dev/sdq|HARD DRIVE|C|")  # noqa: E501


def test_check_hddtemp(mocker):
    """
    Test "check_hddtemp" method must return devices states info.
    """

    expected = {
        "/dev/sda": {
            "template": "ok",
            "priority": 4,
            "data": {
                "device": "/dev/sda",
                "temperature": 28,
                "scale": "C",
                "warning": 40,
                "critical": 65,
            },
        },
    }
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()
    result = checker.check_hddtemp(
        data={"/dev/sda": {"model": "HARD DRIVE", "temperature": "28", "scale": "C"}}
    )

    assert result == expected  # nosec: B101


def test_check_hddtemp__warning(mocker):
    """
    Test "check_hddtemp" method must return devices states info (warning case).
    """

    expected = {
        "/dev/sda": {
            "template": "warning",
            "priority": 2,
            "data": {
                "device": "/dev/sda",
                "temperature": 42,
                "scale": "C",
                "warning": 40,
                "critical": 65,
            },
        },
    }
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()
    result = checker.check_hddtemp(
        data={"/dev/sda": {"model": "HARD DRIVE", "temperature": "42", "scale": "C"}}
    )

    assert result == expected  # nosec: B101


def test_check_hddtemp__critical(mocker):
    """
    Test "check_hddtemp" method must return devices states info (critical case).
    """

    expected = {
        "/dev/sda": {
            "template": "critical",
            "priority": 1,
            "data": {
                "device": "/dev/sda",
                "temperature": 69,
                "scale": "C",
                "warning": 40,
                "critical": 65,
            },
        },
    }
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()
    result = checker.check_hddtemp(
        data={"/dev/sda": {"model": "HARD DRIVE", "temperature": "69", "scale": "C"}}
    )

    assert result == expected  # nosec: B101


def test_check_hddtemp__sleeping_device(mocker):
    """
    Test "check_hddtemp" method must return devices states info (sleeping device case).
    """

    expected = {
        "/dev/sda": {
            "template": "sleeping",
            "priority": 5,
            "data": {
                "device": "/dev/sda",
                "temperature": "SLP",
                "scale": "*",
                "warning": 40,
                "critical": 65,
            },
        },
    }
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()
    result = checker.check_hddtemp(
        data={"/dev/sda": {"model": "HARD DRIVE", "temperature": "SLP", "scale": "*"}}
    )

    assert result == expected  # nosec: B101


def test_check_hddtemp__unknown_device_temperature(mocker):
    """
    Test "check_hddtemp" method must return devices states info
    (unknown device temperature case).
    """

    expected = {
        "/dev/sda": {
            "template": "unknown",
            "priority": 3,
            "data": {
                "device": "/dev/sda",
                "temperature": "UNK",
                "scale": "*",
                "warning": 40,
                "critical": 65,
            },
        },
    }
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()
    result = checker.check_hddtemp(
        data={"/dev/sda": {"model": "HARD DRIVE", "temperature": "UNK", "scale": "*"}}
    )

    assert result == expected  # nosec: B101


def test_check_hddtemp__unknown_device(mocker):
    """
    Test "check_hddtemp" method must return devices states info (unknown device case).
    """

    expected = {
        "/dev/sda": {
            "template": "ok",
            "priority": 4,
            "data": {
                "device": "/dev/sda",
                "temperature": 28,
                "scale": "C",
                "warning": 40,
                "critical": 65,
            },
        },
        "/dev/sdb": {
            "template": "unknown",
            "priority": 3,
            "data": {
                "device": "/dev/sdb",
                "temperature": None,
                "scale": None,
                "warning": 40,
                "critical": 65,
            },
        },
    }
    mocker.patch(
        "sys.argv",
        [
            "check_hddtemp.py",
            "-s",
            "127.0.0.1",
            "-p",
            "7634",
            "-d",
            "/dev/sda, /dev/sdb",
        ],
    )
    checker = CheckHDDTemp()
    result = checker.check_hddtemp(
        data={"/dev/sda": {"model": "HARD DRIVE", "temperature": "28", "scale": "C"}}
    )

    assert result == expected  # nosec: B101
