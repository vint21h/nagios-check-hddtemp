# -*- coding: utf-8 -*-

# nagios-check-hddtemp
# tests/check_hddtemp_test.pyi

from typing import List  # pylint: disable=W0611

from pytest_mock.plugin import MockFixture

__all__: List[str] = ...

def test_get_options(mocker: MockFixture) -> None: ...
def test_get_options__missing_server_option(mocker: MockFixture) -> None: ...
def test_get_options__warning_gte_critical(mocker: MockFixture) -> None: ...
def test_get_data(mocker: MockFixture) -> None: ...
def test_get_data__network_error(mocker: MockFixture) -> None: ...
def test_parse_response(mocker: MockFixture) -> None: ...
def test_parse_response__too_short_error(mocker: MockFixture) -> None: ...
def test_parse_response__parsing_error(mocker: MockFixture) -> None: ...
def test_check_hddtemp(mocker: MockFixture) -> None: ...
def test_check_hddtemp__critical(mocker: MockFixture) -> None: ...
def test_check_hddtemp__sleeping_device(mocker: MockFixture) -> None: ...
def test_check_hddtemp__unknown_device(mocker: MockFixture) -> None: ...
def test_check_hddtemp__unknown_device_temperature(mocker: MockFixture) -> None: ...
def test_check_hddtemp__warning(mocker: MockFixture) -> None: ...
def test_output(mocker: MockFixture) -> None: ...
def test_output__critical(mocker: MockFixture) -> None: ...
def test_output__sleeping(mocker: MockFixture) -> None: ...
def test_output__unknown_device(mocker: MockFixture) -> None: ...
def test_output__unknown_device_temperature(mocker: MockFixture) -> None: ...
def test_output__warning(mocker: MockFixture) -> None: ...
def test_output__critical__performance_data(mocker: MockFixture) -> None: ...
def test_output__performance_data(mocker: MockFixture) -> None: ...
def test_output__sleeping__performance_data(mocker: MockFixture) -> None: ...
def test_output__unknown_device__performance_data(mocker: MockFixture) -> None: ...
def test_output__unknown_device_temperature__performance_data(
    mocker: MockFixture,
) -> None: ...
def test_output__warning__performance_data(mocker: MockFixture) -> None: ...
