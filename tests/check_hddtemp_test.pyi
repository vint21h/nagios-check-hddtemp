# -*- coding: utf-8 -*-

# nagios-check-hddtemp
# tests/check_hddtemp_test.pyi

from typing import List  # pylint: disable=W0611

from pytest_mock.plugin import MockFixture

__all__: List[str] = ...

def test_get_options(mocker: MockFixture) -> None: ...
