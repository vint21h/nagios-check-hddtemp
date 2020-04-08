# -*- coding: utf-8 -*-

# nagios-check-hddtemp
# tests/check_hddtemp_test.py


from __future__ import unicode_literals

from argparse import Namespace

from check_hddtemp import CheckHDDTemp


__all__ = []


def test_get_options(mocker):
    """
    Test "get_options" method must return argparse namespace.
    """

    mocker.patch("sys.argv", ["-s", "127.0.0.1", "-p", "7634"])
    checker = CheckHDDTemp()

    assert isinstance(checker.options, Namespace)  # nosec: B101
