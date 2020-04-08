# -*- coding: utf-8 -*-

# nagios-check-hddtemp
# check_hddtemp.pyi

from typing import List, Dict, Union, Tuple  # pylint: disable=W0611

from argparse import Namespace

__all__: List[str] = ...

class CheckHDDTemp(object):

    HDDTEMP_SLEEPING: str = ...
    HDDTEMP_UNKNOWN: str = ...
    STATUS_CRITICAL: str = ...
    STATUS_WARNING: str = ...
    STATUS_UNKNOWN: str = ...
    STATUS_OK: str = ...
    STATUS_SLEEPING: str = ...
    PRIORITY_CRITICAL: int = ...
    PRIORITY_WARNING: int = ...
    PRIORITY_UNKNOWN: int = ...
    PRIORITY_OK: int = ...
    PRIORITY_SLEEPING: int = ...
    PRIORITY_TO_STATUS: Dict[int, str] = ...
    OUTPUT_TEMPLATES: Dict[str, Dict[str, Union[str, int]]] = ...
    DEFAULT_EXIT_CODE: int = ...
    EXIT_CODES: Dict[str, int] = ...
    PERFORMANCE_DATA_TEMPLATE: str = ...
    options: Union[None, Namespace] = ...
    def __init__(self) -> None: ...
    @staticmethod
    def get_options() -> Namespace: ...
    def get_data(self) -> str: ...
    def parse_response(self, response: str) -> Dict[str, Dict[str, str]]: ...
    def check_hddtemp(
        self, data: Dict[str, Dict[str, str]]
    ) -> Dict[str, Dict[str, Union[str, Dict[str, Union[None, int, str]]]]]: ...
    def output(
        self, states: Dict[str, Dict[str, Union[str, Dict[str, Union[None, int, str]]]]]
    ) -> Tuple[str, int]: ...
    def check(self) -> None: ...


def main() -> None: ...
