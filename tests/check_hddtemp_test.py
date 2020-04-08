# -*- coding: utf-8 -*-

# nagios-check-hddtemp
# tests/check_hddtemp_test.py


from __future__ import unicode_literals

from argparse import Namespace

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

    mocker.patch("sys.argv", ["check_hddtemp.py", "-w", "10", "-c", "5"])
    with pytest.raises(SystemExit):
        CheckHDDTemp()


def test_get_data(mocker):
    """
    Test "get_options" method must return data from server.
    """

    expected = (
        "|/dev/sda|WDC WD10SPCX-24HWST1|SLP|*||/dev/sdb|KINGSTON SH103S3120G|28|C|"
    )
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    mocker.patch("telnetlib.Telnet.open")
    mocker.patch(
        "telnetlib.Telnet.read_all",
        lambda data: b"|/dev/sda|WDC WD10SPCX-24HWST1|SLP|*||/dev/sdb|KINGSTON SH103S3120G|28|C|",  # noqa: E501
    )
    checker = CheckHDDTemp()
    result = checker.get_data()

    assert result == expected  # nosec: B101


def test_get_data__network_error(mocker):
    """
    Test "get_options" method must exit with network error.
    """

    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    with pytest.raises(SystemExit):
        checker = CheckHDDTemp()
        checker.get_data()


def test_parse_response(mocker):
    """
    Test "parse_response" method must return structured data.
    """

    expected = {
        "/dev/sda": {
            "model": "WDC WD10SPCX-24HWST1",
            "temperature": "SLP",
            "scale": "*",
        },
        "/dev/sdb": {
            "model": "KINGSTON SH103S3120G",
            "temperature": "28",
            "scale": "C",
        },
    }
    mocker.patch("sys.argv", ["check_hddtemp.py", "-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()
    result = checker.parse_response(
        response="|/dev/sda|WDC WD10SPCX-24HWST1|SLP|*||/dev/sdb|KINGSTON SH103S3120G|28|C|"  # noqa: E501
    )

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
        checker.parse_response(
            response="|/dev/sda|WDC WD10SPCX-24HWST1|*||/dev/sdb|KINGSTON SH103S3120G|28|C|"  # noqa: E501
        )
