"""
    PyProfiler
        tests/test_utils.py

"""
# Python Dependencies
import pytest

from pstats import SortKey

from PyProfiler import get_default_args
from PyProfiler.utils import default_arg
from PyProfiler.utils import check_keyword
from PyProfiler.utils import is_valid_mode
from PyProfiler.utils import is_valid_sortkey
from PyProfiler.errors import InvalidMode
from PyProfiler.errors import InvalidSortingMethod

from .functions import example
from .functions import example_2
from .functions import Example


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
    pytest.param("INVALID", False, marks=pytest.mark.xfail(raises=InvalidSortingMethod)),
    ('file', True),
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
    (Example().magic, 'profile', ('self', 0, True), {}, True),  # Positional Arg is True
    (Example().magic, 'profile', ('self', 0), {}, True),  # Default Value is True
    (Example().magic, 'profile', ('self',), {}, True),  # Default Value is True
    (Example().magic, 'profile', ('self',), {'profile': True}, True),  # Keyword Arg is True

    (Example().magic, 'profile', ('self',), {'profile': False}, False),  # Keyword Arg is False
    (Example().magic, 'profile', ('self', 0, False), {}, False),  # Positional Arg is False
    (Example().magic, 'wrong', ('self', 0, True), {}, False),  # Wong Keyword (Keyword not present)
    (Example().magic, 'profile', ('self', 0, 1), {}, False),  # Positional Arg is not bool

    # Class Method (wrapper) with Default (False)
    (Example().black, 'debug', ('cls', 0, True), {}, True),  # Positional Arg is True
    (Example().black, 'debug', ('cls', 0), {'debug': True}, True),  # Keyword Arg is True
    (Example().black, 'debug', ('cls', 0, False), {'debug': True}, True),  # Keyword Arg is True

    (Example().black, 'debug', ('cls', 0, False), {}, False),  # Positional Arg is False
    (Example().black, 'debug', ('cls', 0, 1), {}, False),  # Positional Arg is not bool
    (Example().black, 'debug', ('cls', 0), {}, False),  # Default Value is False
    (Example().black, 'debug', ('cls',), {'debug': False}, False),  # Keyword Arg is False

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


@pytest.mark.parametrize('value, expected', [
    ('a', True),
    ('w', True),
    ('ab', True),
    ('wb', True),
    ('at', True),
    ('wt', True),
    pytest.param('r', False, marks=pytest.mark.xfail(raises=InvalidMode)),
    pytest.param('rb', False, marks=pytest.mark.xfail(raises=InvalidMode))
])
def test_mode(value, expected):
    return is_valid_mode(value) is expected
