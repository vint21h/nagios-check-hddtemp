# -*- coding: utf-8 -*-

# nagios-check-hddtemp
# tests/check_hddtemp_test.py


from __future__ import unicode_literals

from argparse import Namespace
from io import StringIO
import socket

import contextlib2
import pytest

from check_hddtemp import CheckHDDTemp, main


__all__ = [
    "test__get_options",
    "test__get_options__missing_server_option",
    "test__get_options__warning_gte_critical",
    "test__get_data",
    "test__get_data__network_error",
    "test__parse_data",
    "test__parse_data__parsing_error",
    "test__parse_data__too_short_error",
    "test__check_data",
    "test__check_data__critical",
    "test__check_data__sleeping_device",
    "test__check_data__unknown_device",
    "test__check_data__unknown_device_temperature",
    "test__check_data__warning",
    "test__get_output",
    "test__get_output__critical",
    "test__get_output__sleeping",
    "test__get_output__unknown_device",
    "test__get_output__unknown_device_temperature",
    "test__get_output__warning",
    "test__get_output__critical__performance_data",
    "test__get_output__performance_data",
    "test__get_output__sleeping__performance_data",
    "test__get_output__unknown_device__performance_data",
    "test__get_output__unknown_device_temperature__performance_data",
    "test__get_output__warning__performance_data",
]


def test__get_options(mocker):
    """
    Test "_get_options" method must return argparse namespace.
    """

    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()

    assert isinstance(checker.options, Namespace)  # nosec: B101


def test__get_options__missing_server_option(mocker):
    """
    Test "_get_options" method must exit with server option missing error.
    """

    out = StringIO()
    mocker.patch("sys.argv", ["check_hddtemp.py"])

    with pytest.raises(SystemExit):
        with contextlib2.redirect_stderr(out):
            CheckHDDTemp()

    assert (  # nosec: B101
        "Required server address option missing" in out.getvalue().strip()
    )


def test__get_options__warning_gte_critical(mocker):
    """
    Test "_get_options" method must exit with warning option
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


def test__get_data(mocker):
    """
    Test "_get_data" method must return data from server.
    """

    expected = "|/dev/sda|HARD DRIVE|27|C|"
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    mocker.patch("telnetlib.Telnet.open")
    mocker.patch(
        "telnetlib.Telnet.read_all", lambda data: b"|/dev/sda|HARD DRIVE|27|C|",
    )

    checker = CheckHDDTemp()
    result = checker._get_data()

    assert result == expected  # nosec: B101


def test__get_data__network_error(mocker):
    """
    Test "_get_data" method must exit with network error.
    """

    out = StringIO()
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    mocker.patch("telnetlib.Telnet.read_all", side_effect=socket.error)
    mocker.patch("telnetlib.Telnet.read_all", side_effect=EOFError)
    checker = CheckHDDTemp()

    with pytest.raises(SystemExit):
        with contextlib2.redirect_stdout(out):
            checker._get_data()

    assert (  # nosec: B101
        "ERROR: Server communication problem" in out.getvalue().strip()
    )


def test__parse_data(mocker):
    """
    Test "_parse_data" method must return structured data.
    """

    expected = {
        "/dev/sda": {"model": "HARD DRIVE", "temperature": "27", "scale": "C"},
    }
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()
    result = checker._parse_data(data="|/dev/sda|HARD DRIVE|27|C|")  # noqa: E501

    assert result == expected  # nosec: B101


def test__parse_data__too_short_error(mocker):
    """
    Test "_parse_data" method must exit with too short response error.
    """

    out = StringIO()
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()

    with pytest.raises(SystemExit):
        with contextlib2.redirect_stdout(out):
            checker._parse_data(data="")

    assert "ERROR: Server response too short" in out.getvalue().strip()  # nosec: B101


def test__parse_data__parsing_error(mocker):
    """
    Test "_parse_data" method must exit with parsing error.
    """

    out = StringIO()
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()

    with pytest.raises(SystemExit):
        with contextlib2.redirect_stdout(out):
            checker._parse_data(data="|/dev/sda|HARD DRIVE|C|")  # noqa: E501

    assert "ERROR: Server response for device" in out.getvalue().strip()  # nosec: B101


def test__check_data(mocker):
    """
    Test "_check_data" method must return devices states info.
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
    result = checker._check_data(
        data={"/dev/sda": {"model": "HARD DRIVE", "temperature": "27", "scale": "C"}}
    )

    assert result == expected  # nosec: B101


def test__check_data__warning(mocker):
    """
    Test "_check_data" method must return devices states info (warning case).
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
    result = checker._check_data(
        data={"/dev/sda": {"model": "HARD DRIVE", "temperature": "42", "scale": "C"}}
    )

    assert result == expected  # nosec: B101


def test__check_data__critical(mocker):
    """
    Test "_check_data" method must return devices states info (critical case).
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
    result = checker._check_data(
        data={"/dev/sda": {"model": "HARD DRIVE", "temperature": "69", "scale": "C"}}
    )

    assert result == expected  # nosec: B101


def test__check_data__sleeping_device(mocker):
    """
    Test "_check_data" method must return devices states info (sleeping device case).
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
    result = checker._check_data(
        data={"/dev/sda": {"model": "HARD DRIVE", "temperature": "SLP", "scale": "*"}}
    )

    assert result == expected  # nosec: B101


def test__check_data__unknown_device_temperature(mocker):
    """
    Test "_check_data" method must return devices states info
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
    result = checker._check_data(
        data={"/dev/sda": {"model": "HARD DRIVE", "temperature": "UNK", "scale": "*"}}
    )

    assert result == expected  # nosec: B101


def test__check_data__unknown_device(mocker):
    """
    Test "_check_data" method must return devices states info (unknown device case).
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
    result = checker._check_data(
        data={"/dev/sda": {"model": "HARD DRIVE", "temperature": "27", "scale": "C"}}
    )

    assert result == expected  # nosec: B101


def test__get_output(mocker):
    """
    Test "_get_output" method must return Nagios and human readable HDD's statuses.
    """

    expected = "OK: device /dev/sda is functional and stable 27C\n"
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()
    result, code = checker._get_output(
        data={
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


def test__get_output__critical(mocker):
    """
    Test "_get_output" method must return Nagios and human readable HDD's statuses
    (critical case).
    """

    expected = "CRITICAL: device /dev/sdb temperature 69C exceeds critical temperature threshold 65C, device /dev/sda is functional and stable 27C\n"  # noqa: E501
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()
    result, code = checker._get_output(
        data={
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


def test__get_output__warning(mocker):
    """
    Test "_get_output" method must return Nagios and human readable HDD's statuses
    (warning case).
    """

    expected = "WARNING: device /dev/sdb temperature 42C exceeds warning temperature threshold 40C, device /dev/sda is functional and stable 27C\n"  # noqa: E501
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()
    result, code = checker._get_output(
        data={
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


def test__get_output__unknown_device(mocker):
    """
    Test "_get_output" method must return Nagios and human readable HDD's statuses
    (unknown device case).
    """

    expected = "UNKNOWN: device /dev/sdb temperature info not found in server response or can't be recognized by hddtemp, device /dev/sda is functional and stable 27C\n"  # noqa: E501
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()
    result, code = checker._get_output(
        data={
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


def test__get_output__unknown_device_temperature(mocker):
    """
    Test "_get_output" method must return Nagios and human readable HDD's statuses
    (unknown device temperature case).
    """

    expected = "UNKNOWN: device /dev/sdb temperature info not found in server response or can't be recognized by hddtemp, device /dev/sda is functional and stable 27C\n"  # noqa: E501
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()
    result, code = checker._get_output(
        data={
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


def test__get_output__sleeping(mocker):
    """
    Test "_get_output" method must return Nagios and human readable HDD's statuses
    (sleeping case).
    """

    expected = "OK: device /dev/sda is functional and stable 27C, device /dev/sdb is sleeping\n"  # noqa: E501
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()
    result, code = checker._get_output(
        data={
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


def test__get_output__performance_data(mocker):
    """
    Test "_get_output" method must return Nagios and human readable HDD's statuses
    with performance data.
    """

    expected = "OK: device /dev/sda is functional and stable 27C | /dev/sda=27\n"
    mocker.patch(
        "sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634", "-P"]
    )
    checker = CheckHDDTemp()
    result, _ = checker._get_output(
        data={
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


def test__get_output__critical__performance_data(mocker):
    """
    Test "_get_output" method must return Nagios and human readable HDD's statuses
    with performance data (critical case).
    """

    expected = "CRITICAL: device /dev/sdb temperature 69C exceeds critical temperature threshold 65C, device /dev/sda is functional and stable 27C | /dev/sdb=69; /dev/sda=27\n"  # noqa: E501
    mocker.patch(
        "sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634", "-P"]
    )
    checker = CheckHDDTemp()
    result, _ = checker._get_output(
        data={
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


def test__get_output__warning__performance_data(mocker):
    """
    Test "_get_output" method must return Nagios and human readable HDD's statuses
    with performance data (warning case).
    """

    expected = "WARNING: device /dev/sdb temperature 42C exceeds warning temperature threshold 40C, device /dev/sda is functional and stable 27C | /dev/sdb=42; /dev/sda=27\n"  # noqa: E501
    mocker.patch(
        "sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634", "-P"]
    )
    checker = CheckHDDTemp()
    result, _ = checker._get_output(
        data={
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


def test__get_output__unknown_device__performance_data(mocker):
    """
    Test "_get_output" method must return Nagios and human readable HDD's statuses
    with performance data (unknown device temperature case).
    """

    expected = "UNKNOWN: device /dev/sdb temperature info not found in server response or can't be recognized by hddtemp, device /dev/sda is functional and stable 27C | /dev/sdb=None; /dev/sda=27\n"  # noqa: E501
    mocker.patch(
        "sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634", "-P"]
    )
    checker = CheckHDDTemp()
    result, _ = checker._get_output(
        data={
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


def test__get_output__unknown_device_temperature__performance_data(mocker):
    """
    Test "_get_output" method must return Nagios and human readable HDD's statuses
    with performance data (unknown device case).
    """

    expected = "UNKNOWN: device /dev/sdb temperature info not found in server response or can't be recognized by hddtemp, device /dev/sda is functional and stable 27C | /dev/sdb=UNK; /dev/sda=27\n"  # noqa: E501
    mocker.patch(
        "sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634", "-P"]
    )
    checker = CheckHDDTemp()
    result, _ = checker._get_output(
        data={
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


def test__get_output__sleeping__performance_data(mocker):
    """
    Test "_get_output" method must return Nagios and human readable HDD's statuses
    with performance data (sleeping case).
    """

    expected = "OK: device /dev/sda is functional and stable 27C, device /dev/sdb is sleeping | /dev/sda=27; /dev/sdb=SLP\n"  # noqa: E501
    mocker.patch(
        "sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634", "-P"]
    )
    checker = CheckHDDTemp()
    result, _ = checker._get_output(
        data={
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
    Test "_get_output" method must return Nagios and human readable HDD's statuses
    (critical case).
    """

    expected = "CRITICAL: device /dev/sdb temperature 69C exceeds critical temperature threshold 65C, device /dev/sda is functional and stable 27C\n"  # noqa: E501
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

    expected = "WARNING: device /dev/sdb temperature 42C exceeds warning temperature threshold 40C, device /dev/sda is functional and stable 27C\n"  # noqa: E501
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

    expected = "UNKNOWN: device /dev/sdb temperature info not found in server response or can't be recognized by hddtemp, device /dev/sda is functional and stable 27C\n"  # noqa: E501
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
    Test "_get_output" method must return Nagios and human readable HDD's statuses
    (unknown device temperature case).
    """

    expected = "UNKNOWN: device /dev/sdb temperature info not found in server response or can't be recognized by hddtemp, device /dev/sda is functional and stable 27C\n"  # noqa: E501
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

    expected = "CRITICAL: device /dev/sdb temperature 69C exceeds critical temperature threshold 65C, device /dev/sda is functional and stable 27C | /dev/sdb=69; /dev/sda=27\n"  # noqa: E501
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

    expected = "WARNING: device /dev/sdb temperature 42C exceeds warning temperature threshold 40C, device /dev/sda is functional and stable 27C | /dev/sdb=42; /dev/sda=27\n"  # noqa: E501
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

    expected = "UNKNOWN: device /dev/sdb temperature info not found in server response or can't be recognized by hddtemp, device /dev/sda is functional and stable 27C | /dev/sdb=None; /dev/sda=27\n"  # noqa: E501
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

    expected = "UNKNOWN: device /dev/sdb temperature info not found in server response or can't be recognized by hddtemp, device /dev/sda is functional and stable 27C | /dev/sdb=UNK; /dev/sda=27\n"  # noqa: E501
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


def test_main(mocker):
    """
    Test "main" function must print Nagios and human readable HDD's statuses.
    """

    out = StringIO()
    expected = "OK: device /dev/sda is functional and stable 27C\n"  # noqa: E501
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    mocker.patch("telnetlib.Telnet.open")
    mocker.patch(
        "telnetlib.Telnet.read_all", lambda data: b"|/dev/sda|HARD DRIVE|27|C|",
    )

    with pytest.raises(SystemExit) as excinfo:
        with contextlib2.redirect_stdout(out):
            main()

    assert out.getvalue() == expected  # nosec: B101
    assert excinfo.value.args == (0,)  # nosec: B101
