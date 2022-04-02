"""
    PyProfiler
        tests/test_utils.py

"""
import pytest

from pstats import SortKey

from PyProfiler import get_default_args
from PyProfiler.utils import is_valid_sortkey, check_keyword, default_arg


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
    # Function without Default Value
    (example, 'debug', (), {'debug': True}, True),  # Keyword Arg is True
    (example, 'debug', (0, 0, True), {}, True),  # Positional Arg is True

    (example, 'debug', (0, 0, False), {}, False),  # Positional Arg is False
    (example, 'debug', (), {}, False),  # No Default Value Specified
    (example, 'verbose', (), {'verbose': True}, False),  # Wong Keyword (Keyword not present)
    (example, 'debug', (), {'debug': False}, False),  # Keyword Arg is False

    # Function with Default Value (True)
    (example_2, 'verbose', (), {}, True),  # Default Value is True
    (example_2, 'verbose', (0, 0, True), {}, True),  # Positional Arg is True

    (example_2, 'verbose', (), {'verbose': False}, False),  # Keyword Arg is False
    (example_2, 'verbose', (0, 0, False), {}, False),  # Positional Arg is False
    (example_2, 'debug', (0, 0, True), {}, False),  # Wong Keyword (Keyword not present)
    (example_2, 'verbose', (0, 0, 1), {}, False),  # Positional Arg is not bool
    (example_2, 'verbose', (0, 0), {'verbose': False}, False),  # Keyword Arg is False
    (example_2, 'verbose', (0, 0), {'verbose': 1}, False),  # Positional Arg is not bool

    # Method with Default (True)
    (Example().magic, 'profile', (0, True), {}, True),  # Positional Arg is True
    (Example().magic, 'profile', (0,), {}, True),  # Default Value is True
    (Example().magic, 'profile', (), {}, True),  # Default Value is True
    (Example().magic, 'profile', (), {'profile': True}, True),  # Keyword Arg is True

    (Example().magic, 'profile', (), {'profile': False}, False),  # Keyword Arg is False
    (Example().magic, 'profile', (0, False), {}, False),  # Positional Arg is False
    (Example().magic, 'wrong', (0, True), {}, False),  # Wong Keyword (Keyword not present)
    (Example().magic, 'profile', (0, 1), {}, False),  # Positional Arg is not bool

    # Class Method (wrapper) with Default (False)
    (Example().black, 'debug', (0, True), {}, True),  # Positional Arg is True
    (Example().black, 'debug', (0, ), {'debug': True}, True),  # Keyword Arg is True
    (Example().black, 'debug', (0, False), {'debug': True}, True),  # Keyword Arg is True

    (Example().black, 'debug', (0, False), {}, False),  # Positional Arg is False
    (Example().black, 'debug', (0, 1), {}, False),  # Positional Arg is not bool
    (Example().black, 'debug', (0,), {}, False),  # Default Value is False
    (Example().black, 'debug', (), {'debug': False}, False),  # Keyword Arg is False

    # Static Method (wrapper) without Default Value
    (Example().lady, 'profile', (0, True), {}, True),  # Positional Arg is True
    (Example().lady, 'profile', (), {'profile': True}, True),  # Keyword Arg is True

    (Example().lady, 'profile', (0, False), {}, False),  # Positional Arg is False
    (Example().lady, 'profile', (0,), {}, False),  # No Default Value --> False
    (Example().lady, 'profile', (0, 1), {}, False),  # Positional Arg is not bool
    (Example().lady, 'profile', (), {}, False),  # No Default Value --> False
    (Example().lady, 'profile', (), {'profile': False}, False),  # Keyword Arg is False
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


@pytest.mark.parametrize('function, keyword, default, expected', [
    (example, 'debug', True, True),
    (example, 'debug',  False, False),
    (example_2, 'verbose', True, True),
    (example_2, 'verbose', False, True),
    (example_2, '', True, True),
    (example_2, '', False, False),
    (Example.magic, 'profile', True, True),
    (Example.magic, 'profile', False, True),
    (Example.magic, '', True, True),
    (Example.magic, '', False, False),
    (Example.black, 'debug', False, False),
    (Example.black, 'debug', True, False),
    (Example.black, '', False, False),
    (Example.black, '', True, True),
    (Example.lady, 'profile', True, True),
    (Example.lady, 'profile', False, False),
    (Example.lady, '', True, True),
    (Example.lady, '', False, False),
])
def test_default_keyvalue(function, keyword, default, expected):
    assert default_arg(function, keyword, default) is expected
