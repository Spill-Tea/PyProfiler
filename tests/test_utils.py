"""
    tests/test_utils.py

"""
import pytest

from pstats import SortKey

from PyProfiler import get_default_args
from PyProfiler.utils import is_valid_sortkey, check_keyword


def example(a, b, debug):
    return a + b


def example_2(a: int = 1, b: int = 2, verbose: bool = True):
    return a + b


class Example:
    def __init__(self):
        pass

    @classmethod
    def black(cls, b, debug=False):
        return b

    def magic(self, a, profile=True):
        return a

    @staticmethod
    def lady(a, profile):
        return a


@pytest.mark.parametrize('value, expected', [
    (SortKey.CALLS, True), ('calls', True),
    (SortKey.PCALLS, True), ('pcalls', True),
    (SortKey.CUMULATIVE, True), ('cumulative', True), ('cumtime', True),
    (SortKey.NFL, True), ('nfl', True),
    (SortKey.NAME, True), ('name', True),
    (SortKey.STDNAME, True), ('stdname', True),
    (SortKey.FILENAME, True), ('filename', True), ('module', True),
    (SortKey.LINE, True), ('line', True),
    (SortKey.TIME, True), ('time', True), ('tottime', True),
    ('INVALID', False), ('file', True),
])
def test_sortkey(value, expected):
    assert is_valid_sortkey(value) is expected


@pytest.mark.parametrize('function, keyword, args, kwargs, expected', [
    (example, 'debug', (), {'debug': True}, True),
    (example, 'debug', (), {}, False),
    (example, 'verbose', (), {'verbose': True}, False),
    (example, 'debug', (), {'debug': False}, False),
    (example, 'debug', (0, 0, True), {}, True),
    (example, 'debug', (0, 0, False), {}, False),
    (example_2, 'verbose', (), {}, True),
    (example_2, 'verbose', (), {'verbose': False}, False),
    (example_2, 'verbose', (0, 0, False), {}, False),
    (example_2, 'verbose', (0, 0, True), {}, True),
    (example_2, 'debug', (0, 0, True), {}, False),
    (example_2, 'verbose', (0, 0, 1), {}, False),
    (example_2, 'verbose', (0, 0), {'verbose': False}, False),
    (example_2, 'verbose', (0, 0), {'verbose': 1}, False),
    (Example().magic, 'profile', (0, True), {}, True),
    (Example().magic, 'profile', (0, False), {}, False),
    (Example().magic, 'profile', (0,), {}, True),
    (Example().magic, 'profile', (), {}, True),
    (Example().magic, 'profile', (), {'profile': True}, True),
    (Example().magic, 'profile', (), {'profile': False}, False),
    (Example().black, 'debug', (0, True), {}, True),
    (Example().black, 'debug', (0, False), {}, False),
    (Example().black, 'debug', (0,), {}, False),
    (Example().black, 'debug', (), {'debug': False}, False),
    (Example().lady, 'profile', (0, True), {}, True),
    (Example().lady, 'profile', (0, False), {}, False),
    (Example().lady, 'profile', (0,), {}, False),
    (Example().lady, 'profile', (), {}, False),
    (Example().lady, 'profile', (), {'profile': True}, True),
    (Example().lady, 'profile', (), {'profile': False}, False),
])
def test_keyword(function, keyword, args, kwargs, expected):
    assert check_keyword(function, keyword, *args, **kwargs) is expected


@pytest.mark.parametrize('function, expected', [
    (example, dict(zip(['a', 'b', 'debug'], [None] * 3))),
    (example_2, dict(zip(['a', 'b', 'verbose'], [1, 2, True]))),
    (Example.magic, dict(zip(['self', 'a', 'profile'], [None, None, True]))),
    (Example.black, dict(zip(['b', 'debug'], [None, False]))),  # classmethod wrapper modifies inspection of method
    (Example.lady, dict(zip(['a', 'profile'], [None] * 2))),
])
def test_default_values(function, expected):
    assert get_default_args(function, None) == expected