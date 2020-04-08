# -*- coding: utf-8 -*-

# nagios-check-hddtemp
# tests/check_hddtemp_test.py


from __future__ import unicode_literals

from argparse import Namespace
from io import StringIO
import socket

import contextlib2
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
    "test_output",
    "test_output__critical",
    "test_output__sleeping",
    "test_output__unknown_device",
    "test_output__unknown_device_temperature",
    "test_output__warning",
    "test_output__critical__performance_data",
    "test_output__performance_data",
    "test_output__sleeping__performance_data",
    "test_output__unknown_device__performance_data",
    "test_output__unknown_device_temperature__performance_data",
    "test_output__warning__performance_data",
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

    out = StringIO()
    mocker.patch("sys.argv", ["check_hddtemp.py"])

    with pytest.raises(SystemExit):
        with contextlib2.redirect_stderr(out):
            CheckHDDTemp()

    assert (  # nosec: B101
        "Required server address option missing" in out.getvalue().strip()
    )


def test_get_options__warning_gte_critical(mocker):
    """
    Test "get_options" method must exit with warning option
    greater or equal than critical error.
    """

    out = StringIO()
    mocker.patch(
        "sys.argv", ["check_hddtemp.py", "-s" "127.0.0.1", "-w", "65", "-c", "40"]
    )

    with pytest.raises(SystemExit):
        with contextlib2.redirect_stderr(out):
            CheckHDDTemp()

    assert (  # nosec: B101
        "Warning temperature option value must be less than critical option value"
        in out.getvalue().strip()
    )


def test_get_data(mocker):
    """
    Test "get_options" method must return data from server.
    """

    expected = "|/dev/sda|HARD DRIVE|27|C|"
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    mocker.patch("telnetlib.Telnet.open")
    mocker.patch(
        "telnetlib.Telnet.read_all", lambda data: b"|/dev/sda|HARD DRIVE|27|C|",
    )

    checker = CheckHDDTemp()
    result = checker.get_data()

    assert result == expected  # nosec: B101


def test_get_data__network_error(mocker):
    """
    Test "get_options" method must exit with network error.
    """

    out = StringIO()
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    mocker.patch("telnetlib.Telnet.read_all", side_effect=socket.error)
    mocker.patch("telnetlib.Telnet.read_all", side_effect=EOFError)
    checker = CheckHDDTemp()

    with pytest.raises(SystemExit):
        with contextlib2.redirect_stdout(out):
            checker.get_data()

    assert (  # nosec: B101
        "ERROR: Server communication problem" in out.getvalue().strip()
    )


def test_parse_response(mocker):
    """
    Test "parse_response" method must return structured data.
    """

    expected = {
        "/dev/sda": {"model": "HARD DRIVE", "temperature": "27", "scale": "C"},
    }
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()
    result = checker.parse_response(response="|/dev/sda|HARD DRIVE|27|C|")  # noqa: E501

    assert result == expected  # nosec: B101


def test_parse_response__too_short_error(mocker):
    """
    Test "parse_response" method must exit with too short response error.
    """

    out = StringIO()
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()

    with pytest.raises(SystemExit):
        with contextlib2.redirect_stdout(out):
            checker.parse_response(response="")

    assert "ERROR: Server response too short" in out.getvalue().strip()  # nosec: B101


def test_parse_response__parsing_error(mocker):
    """
    Test "parse_response" method must exit with parsing error.
    """

    out = StringIO()
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()

    with pytest.raises(SystemExit):
        with contextlib2.redirect_stdout(out):
            checker.parse_response(response="|/dev/sda|HARD DRIVE|C|")  # noqa: E501

    assert "ERROR: Server response for device" in out.getvalue().strip()  # nosec: B101


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
                "temperature": 27,
                "scale": "C",
                "warning": 40,
                "critical": 65,
            },
        },
    }
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()
    result = checker.check_hddtemp(
        data={"/dev/sda": {"model": "HARD DRIVE", "temperature": "27", "scale": "C"}}
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
                "temperature": 27,
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
        data={"/dev/sda": {"model": "HARD DRIVE", "temperature": "27", "scale": "C"}}
    )

    assert result == expected  # nosec: B101


def test_output(mocker):
    """
    Test "output" method must return Nagios and human readable HDD's statuses.
    """

    expected = "OK: device /dev/sda is functional and stable 27C\n"
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()
    result, code = checker.output(
        states={
            "/dev/sda": {
                "template": "ok",
                "priority": 4,
                "data": {
                    "device": "/dev/sda",
                    "temperature": 27,
                    "scale": "C",
                    "warning": 40,
                    "critical": 65,
                },
            },
        }
    )

    assert result == expected  # nosec: B101
    assert code == 0  # nosec: B101


def test_output__critical(mocker):
    """
    Test "output" method must return Nagios and human readable HDD's statuses
    (critical case).
    """

    expected = "CRITICAL: device /dev/sda is functional and stable 27C, device /dev/sdb temperature 69C exceeds critical temperature threshold 65C\n"  # noqa: E501
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()
    result, code = checker.output(
        states={
            "/dev/sda": {
                "template": "ok",
                "priority": 4,
                "data": {
                    "device": "/dev/sda",
                    "temperature": 27,
                    "scale": "C",
                    "warning": 40,
                    "critical": 65,
                },
            },
            "/dev/sdb": {
                "template": "critical",
                "priority": 1,
                "data": {
                    "device": "/dev/sdb",
                    "temperature": 69,
                    "scale": "C",
                    "warning": 40,
                    "critical": 65,
                },
            },
        }
    )

    assert result == expected  # nosec: B101
    assert code == 2  # nosec: B101


def test_output__warning(mocker):
    """
    Test "output" method must return Nagios and human readable HDD's statuses
    (warning case).
    """

    expected = "WARNING: device /dev/sda is functional and stable 27C, device /dev/sdb temperature 42C exceeds warning temperature threshold 40C\n"  # noqa: E501
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()
    result, code = checker.output(
        states={
            "/dev/sda": {
                "template": "ok",
                "priority": 4,
                "data": {
                    "device": "/dev/sda",
                    "temperature": 27,
                    "scale": "C",
                    "warning": 40,
                    "critical": 65,
                },
            },
            "/dev/sdb": {
                "template": "warning",
                "priority": 2,
                "data": {
                    "device": "/dev/sdb",
                    "temperature": 42,
                    "scale": "C",
                    "warning": 40,
                    "critical": 65,
                },
            },
        }
    )

    assert result == expected  # nosec: B101
    assert code == 1  # nosec: B101


def test_output__unknown_device(mocker):
    """
    Test "output" method must return Nagios and human readable HDD's statuses
    (unknown device case).
    """

    expected = "UNKNOWN: device /dev/sda is functional and stable 27C, device /dev/sdb temperature info not found in server response or can't be recognized by hddtemp\n"  # noqa: E501
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()
    result, code = checker.output(
        states={
            "/dev/sda": {
                "template": "ok",
                "priority": 4,
                "data": {
                    "device": "/dev/sda",
                    "temperature": 27,
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
    )

    assert result == expected  # nosec: B101
    assert code == 3  # nosec: B101


def test_output__unknown_device_temperature(mocker):
    """
    Test "output" method must return Nagios and human readable HDD's statuses
    (unknown device temperature case).
    """

    expected = "UNKNOWN: device /dev/sda is functional and stable 27C, device /dev/sdb temperature info not found in server response or can't be recognized by hddtemp\n"  # noqa: E501
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()
    result, code = checker.output(
        states={
            "/dev/sda": {
                "template": "ok",
                "priority": 4,
                "data": {
                    "device": "/dev/sda",
                    "temperature": 27,
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
                    "temperature": "UNK",
                    "scale": "*",
                    "warning": 40,
                    "critical": 65,
                },
            },
        }
    )

    assert result == expected  # nosec: B101
    assert code == 3  # nosec: B101


def test_output__sleeping(mocker):
    """
    Test "output" method must return Nagios and human readable HDD's statuses
    (sleeping case).
    """

    expected = "OK: device /dev/sda is functional and stable 27C, device /dev/sdb is sleeping\n"  # noqa: E501
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()
    result, code = checker.output(
        states={
            "/dev/sda": {
                "template": "ok",
                "priority": 4,
                "data": {
                    "device": "/dev/sda",
                    "temperature": 27,
                    "scale": "C",
                    "warning": 40,
                    "critical": 65,
                },
            },
            "/dev/sdb": {
                "template": "sleeping",
                "priority": 5,
                "data": {
                    "device": "/dev/sdb",
                    "temperature": "SLP",
                    "scale": "C",
                    "warning": 40,
                    "critical": 65,
                },
            },
        }
    )

    assert result == expected  # nosec: B101
    assert code == 0  # nosec: B101


def test_output__performance_data(mocker):
    """
    Test "output" method must return Nagios and human readable HDD's statuses
    with performance data.
    """

    expected = "OK: device /dev/sda is functional and stable 27C | /dev/sda=27\n"
    mocker.patch(
        "sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634", "-P"]
    )
    checker = CheckHDDTemp()
    result, _ = checker.output(
        states={
            "/dev/sda": {
                "template": "ok",
                "priority": 4,
                "data": {
                    "device": "/dev/sda",
                    "temperature": 27,
                    "scale": "C",
                    "warning": 40,
                    "critical": 65,
                },
            },
        }
    )

    assert result == expected  # nosec: B101


def test_output__critical__performance_data(mocker):
    """
    Test "output" method must return Nagios and human readable HDD's statuses
    with performance data (critical case).
    """

    expected = "CRITICAL: device /dev/sda is functional and stable 27C, device /dev/sdb temperature 69C exceeds critical temperature threshold 65C | /dev/sda=27; /dev/sdb=69\n"  # noqa: E501
    mocker.patch(
        "sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634", "-P"]
    )
    checker = CheckHDDTemp()
    result, _ = checker.output(
        states={
            "/dev/sda": {
                "template": "ok",
                "priority": 4,
                "data": {
                    "device": "/dev/sda",
                    "temperature": 27,
                    "scale": "C",
                    "warning": 40,
                    "critical": 65,
                },
            },
            "/dev/sdb": {
                "template": "critical",
                "priority": 1,
                "data": {
                    "device": "/dev/sdb",
                    "temperature": 69,
                    "scale": "C",
                    "warning": 40,
                    "critical": 65,
                },
            },
        }
    )

    assert result == expected  # nosec: B101


def test_output__warning__performance_data(mocker):
    """
    Test "output" method must return Nagios and human readable HDD's statuses
    with performance data (warning case).
    """

    expected = "WARNING: device /dev/sda is functional and stable 27C, device /dev/sdb temperature 42C exceeds warning temperature threshold 40C | /dev/sda=27; /dev/sdb=42\n"  # noqa: E501
    mocker.patch(
        "sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634", "-P"]
    )
    checker = CheckHDDTemp()
    result, _ = checker.output(
        states={
            "/dev/sda": {
                "template": "ok",
                "priority": 4,
                "data": {
                    "device": "/dev/sda",
                    "temperature": 27,
                    "scale": "C",
                    "warning": 40,
                    "critical": 65,
                },
            },
            "/dev/sdb": {
                "template": "warning",
                "priority": 2,
                "data": {
                    "device": "/dev/sdb",
                    "temperature": 42,
                    "scale": "C",
                    "warning": 40,
                    "critical": 65,
                },
            },
        }
    )

    assert result == expected  # nosec: B101


def test_output__unknown_device__performance_data(mocker):
    """
    Test "output" method must return Nagios and human readable HDD's statuses
    with performance data (unknown device temperature case).
    """

    expected = "UNKNOWN: device /dev/sda is functional and stable 27C, device /dev/sdb temperature info not found in server response or can't be recognized by hddtemp | /dev/sda=27; /dev/sdb=None\n"  # noqa: E501
    mocker.patch(
        "sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634", "-P"]
    )
    checker = CheckHDDTemp()
    result, _ = checker.output(
        states={
            "/dev/sda": {
                "template": "ok",
                "priority": 4,
                "data": {
                    "device": "/dev/sda",
                    "temperature": 27,
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
    )

    assert result == expected  # nosec: B101


def test_output__unknown_device_temperature__performance_data(mocker):
    """
    Test "output" method must return Nagios and human readable HDD's statuses
    with performance data (unknown device case).
    """

    expected = "UNKNOWN: device /dev/sda is functional and stable 27C, device /dev/sdb temperature info not found in server response or can't be recognized by hddtemp | /dev/sda=27; /dev/sdb=UNK\n"  # noqa: E501
    mocker.patch(
        "sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634", "-P"]
    )
    checker = CheckHDDTemp()
    result, _ = checker.output(
        states={
            "/dev/sda": {
                "template": "ok",
                "priority": 4,
                "data": {
                    "device": "/dev/sda",
                    "temperature": 27,
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
                    "temperature": "UNK",
                    "scale": "*",
                    "warning": 40,
                    "critical": 65,
                },
            },
        }
    )

    assert result == expected  # nosec: B101


def test_output__sleeping__performance_data(mocker):
    """
    Test "output" method must return Nagios and human readable HDD's statuses
    with performance data (sleeping case).
    """

    expected = "OK: device /dev/sda is functional and stable 27C, device /dev/sdb is sleeping | /dev/sda=27; /dev/sdb=SLP\n"  # noqa: E501
    mocker.patch(
        "sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634", "-P"]
    )
    checker = CheckHDDTemp()
    result, _ = checker.output(
        states={
            "/dev/sda": {
                "template": "ok",
                "priority": 4,
                "data": {
                    "device": "/dev/sda",
                    "temperature": 27,
                    "scale": "C",
                    "warning": 40,
                    "critical": 65,
                },
            },
            "/dev/sdb": {
                "template": "sleeping",
                "priority": 5,
                "data": {
                    "device": "/dev/sdb",
                    "temperature": "SLP",
                    "scale": "C",
                    "warning": 40,
                    "critical": 65,
                },
            },
        }
    )

    assert result == expected  # nosec: B101


def test_check(mocker):
    """
    Test "check" method must return Nagios and human readable HDD's statuses.
    """

    expected = "OK: device /dev/sda is functional and stable 27C\n"
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    mocker.patch("telnetlib.Telnet.open")
    mocker.patch(
        "telnetlib.Telnet.read_all", lambda data: b"|/dev/sda|HARD DRIVE|27|C|",
    )
    checker = CheckHDDTemp()
    result, code = checker.check()

    assert result == expected  # nosec: B101
    assert code == 0  # nosec: B101


def test_check__critical(mocker):
    """
    Test "output" method must return Nagios and human readable HDD's statuses
    (critical case).
    """

    expected = "CRITICAL: device /dev/sda is functional and stable 27C, device /dev/sdb temperature 69C exceeds critical temperature threshold 65C\n"  # noqa: E501
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    mocker.patch("telnetlib.Telnet.open")
    mocker.patch(
        "telnetlib.Telnet.read_all",
        lambda data: b"|/dev/sda|HARD DRIVE|27|C||/dev/sdb|HARD DRIVE|69|C|",
    )
    checker = CheckHDDTemp()

    result, code = checker.check()

    assert result == expected  # nosec: B101
    assert code == 2  # nosec: B101


def test_check__warning(mocker):
    """
    Test "check" method must return Nagios and human readable HDD's statuses
    (warning case).
    """

    expected = "WARNING: device /dev/sda is functional and stable 27C, device /dev/sdb temperature 42C exceeds warning temperature threshold 40C\n"  # noqa: E501
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    mocker.patch("telnetlib.Telnet.open")
    mocker.patch(
        "telnetlib.Telnet.read_all",
        lambda data: b"|/dev/sda|HARD DRIVE|27|C||/dev/sdb|HARD DRIVE|42|C|",
    )
    checker = CheckHDDTemp()
    result, code = checker.check()

    assert result == expected  # nosec: B101
    assert code == 1  # nosec: B101


def test_check__unknown_device(mocker):
    """
    Test "check" method must return Nagios and human readable HDD's statuses
    (unknown device case).
    """

    expected = "UNKNOWN: device /dev/sda is functional and stable 27C, device /dev/sdb temperature info not found in server response or can't be recognized by hddtemp\n"  # noqa: E501
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
    mocker.patch("telnetlib.Telnet.open")
    mocker.patch(
        "telnetlib.Telnet.read_all", lambda data: b"|/dev/sda|HARD DRIVE|27|C|",
    )
    result, code = checker.check()

    assert result == expected  # nosec: B101
    assert code == 3  # nosec: B101


def test_check__unknown_device_temperature(mocker):
    """
    Test "output" method must return Nagios and human readable HDD's statuses
    (unknown device temperature case).
    """

    expected = "UNKNOWN: device /dev/sda is functional and stable 27C, device /dev/sdb temperature info not found in server response or can't be recognized by hddtemp\n"  # noqa: E501
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()
    mocker.patch("telnetlib.Telnet.open")
    mocker.patch(
        "telnetlib.Telnet.read_all",
        lambda data: b"|/dev/sda|HARD DRIVE|27|C||/dev/sdb|HARD DRIVE|UNK|*|",
    )
    result, code = checker.check()

    assert result == expected  # nosec: B101
    assert code == 3  # nosec: B101


def test_check__sleeping(mocker):
    """
    Test "check" method must return Nagios and human readable HDD's statuses
    (sleeping case).
    """

    expected = "OK: device /dev/sda is functional and stable 27C, device /dev/sdb is sleeping\n"  # noqa: E501
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()
    mocker.patch("telnetlib.Telnet.open")
    mocker.patch(
        "telnetlib.Telnet.read_all",
        lambda data: b"|/dev/sda|HARD DRIVE|27|C||/dev/sdb|HARD DRIVE|SLP|*|",
    )
    result, code = checker.check()

    assert result == expected  # nosec: B101
    assert code == 0  # nosec: B101


def test_check__performance_data(mocker):
    """
    Test "check" method must return Nagios and human readable HDD's statuses
    with performance data.
    """

    expected = "OK: device /dev/sda is functional and stable 27C | /dev/sda=27\n"
    mocker.patch(
        "sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634", "-P"]
    )
    checker = CheckHDDTemp()
    mocker.patch("telnetlib.Telnet.open")
    mocker.patch(
        "telnetlib.Telnet.read_all", lambda data: b"|/dev/sda|HARD DRIVE|27|C|",
    )
    result, code = checker.check()

    assert result == expected  # nosec: B101
    assert code == 0  # nosec: B101


def test_check__critical__performance_data(mocker):
    """
    Test "check" method must return Nagios and human readable HDD's statuses
    with performance data (critical case).
    """

    expected = "CRITICAL: device /dev/sda is functional and stable 27C, device /dev/sdb temperature 69C exceeds critical temperature threshold 65C | /dev/sda=27; /dev/sdb=69\n"  # noqa: E501
    mocker.patch(
        "sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634", "-P"]
    )
    mocker.patch("telnetlib.Telnet.open")
    mocker.patch(
        "telnetlib.Telnet.read_all",
        lambda data: b"|/dev/sda|HARD DRIVE|27|C||/dev/sdb|HARD DRIVE|69|C|",
    )
    checker = CheckHDDTemp()
    result, code = checker.check()

    assert result == expected  # nosec: B101
    assert code == 2  # nosec: B101


def test_check__warning__performance_data(mocker):
    """
    Test "check" method must return Nagios and human readable HDD's statuses
    with performance data (warning case).
    """

    expected = "WARNING: device /dev/sda is functional and stable 27C, device /dev/sdb temperature 42C exceeds warning temperature threshold 40C | /dev/sda=27; /dev/sdb=42\n"  # noqa: E501
    mocker.patch(
        "sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634", "-P"]
    )
    mocker.patch("telnetlib.Telnet.open")
    mocker.patch(
        "telnetlib.Telnet.read_all",
        lambda data: b"|/dev/sda|HARD DRIVE|27|C||/dev/sdb|HARD DRIVE|42|C|",
    )
    checker = CheckHDDTemp()
    result, code = checker.check()

    assert result == expected  # nosec: B101
    assert code == 1  # nosec: B101


def test_check__unknown_device__performance_data(mocker):
    """
    Test "check" method must return Nagios and human readable HDD's statuses
    with performance data (unknown device case).
    """

    expected = "UNKNOWN: device /dev/sda is functional and stable 27C, device /dev/sdb temperature info not found in server response or can't be recognized by hddtemp | /dev/sda=27; /dev/sdb=None\n"  # noqa: E501
    mocker.patch(
        "sys.argv",
        [
            "check_hddtemp.py",
            "-s",
            "127.0.0.1",
            "-p",
            "7634",
            "-P",
            "-d",
            "/dev/sda, /dev/sdb",
        ],
    )
    mocker.patch("telnetlib.Telnet.open")
    mocker.patch(
        "telnetlib.Telnet.read_all", lambda data: b"|/dev/sda|HARD DRIVE|27|C|",
    )
    checker = CheckHDDTemp()
    result, code = checker.check()

    assert result == expected  # nosec: B101
    assert code == 3  # nosec: B101


def test_check__unknown_device_temperature__performance_data(mocker):
    """
    Test "check" method must return Nagios and human readable HDD's statuses
    with performance data (unknown device temperature case).
    """

    expected = "UNKNOWN: device /dev/sda is functional and stable 27C, device /dev/sdb temperature info not found in server response or can't be recognized by hddtemp | /dev/sda=27; /dev/sdb=UNK\n"  # noqa: E501
    mocker.patch(
        "sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634", "-P"]
    )
    mocker.patch("telnetlib.Telnet.open")
    mocker.patch(
        "telnetlib.Telnet.read_all",
        lambda data: b"|/dev/sda|HARD DRIVE|27|C||/dev/sdb|HARD DRIVE|UNK|*|",
    )
    checker = CheckHDDTemp()
    result, code = checker.check()

    assert result == expected  # nosec: B101
    assert code == 3  # nosec: B101


def test_check__sleeping__performance_data(mocker):
    """
    Test "check" method must return Nagios and human readable HDD's statuses
    with performance data (sleeping case).
    """

    expected = "OK: device /dev/sda is functional and stable 27C, device /dev/sdb is sleeping | /dev/sda=27; /dev/sdb=SLP\n"  # noqa: E501
    mocker.patch(
        "sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634", "-P"]
    )
    mocker.patch("telnetlib.Telnet.open")
    mocker.patch(
        "telnetlib.Telnet.read_all",
        lambda data: b"|/dev/sda|HARD DRIVE|27|C||/dev/sdb|HARD DRIVE|SLP|*|",
    )
    checker = CheckHDDTemp()
    result, code = checker.check()

    assert result == expected  # nosec: B101
    assert code == 0  # nosec: B101
