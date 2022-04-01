"""
    PyProfiler/utils.py
    MIT License

    Copyright (c) 2022 Spill-Tea

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

"""
# Python Dependencies
from sys import stdout
from pstats import SortKey, Stats
from typing import Any, Callable, IO

from inspect import Parameter
from inspect import getfullargspec, signature


def get_default_args(function: Callable, default: Any) -> dict:
    """Retrieve all Default Values of a Given Function.
    Args
        function (Callable)
            A function to inspect
        default (Any)
            Define a Default Value when none exists
    Returns (dict)
        A Dictionary of {args: default value} of a given function.

    """
    d = signature(function).parameters.items()
    return {key: val.default if val.default != Parameter.empty else default for key, val in d}


def default_arg(function: Callable, keyword: str, default: Any = None) -> Any:
    """Retrieve the Default Value of the Specified Keyword Argument.
    Args
        function (Callable)
            A function to inspect
        keyword (str)
            keyword argument to find.
        default (Any)
            Define a Default Value when none exists
    Returns (Any)
        The default value of a given keyword, from the specified function.
        NOTE: If the function does not have a given keyword, the default value is returned.

    """
    try:
        ret_val = signature(function).parameters[keyword]
        if ret_val.default == Parameter.empty:
            return default
        return ret_val.default
    except KeyError:
        return default


def check_keyword(function: Callable, keyword: str, *args, **kwargs):
    """Introspection Method to retrieve value of keyword. Assumes keyword should be a boolean."""
    specs = getfullargspec(function)

    # Function must have the specified Keyword Argument
    has_keyword = keyword in specs.args
    if has_keyword is False:
        return False

    # Check keyword Args --> Positional Args --> Default Values --> False
    key_value = kwargs.get(
        keyword,
        dict(zip(specs.args, args)).get(
            keyword,
            default_arg(function, keyword, False)
        )
    )

    return has_keyword and key_value and isinstance(key_value, bool)


def is_valid_sortkey(value: Any) -> bool:
    """Test if the value is a valid Sorting Method accepted by cProfile and pstats Stats libraries."""
    try:
        # SortKey is an enum class. If value is a string, this will raise a type error.
        isvalid = value in SortKey
    except TypeError:
        isvalid = False

    # Then Check accepted / valid string arguments
    isvalid |= value in [
        'calls', 'cumtime', 'cumulative', 'file', 'filename', 'line', 'module',
        'name', 'ncalls', 'nfl', 'pcalls', 'stdname', 'time', 'tottime'
    ]

    return isvalid


def is_valid_mode(value: str):
    """Test if the value is a valid File Opening Mode."""
    # accepted_modes = [
    #     'w', 'w+', 'wb', 'bw', 'w+b', 'bw+', 'wt', 'tw', 'w+t', 'tw+',
    #     'a', 'a+', 'ab', 'ba', 'a+b', 'ba+', 'at', 'ta', 'a+t', 'ta+',
    #     ]
    accepted_modes = [
        'w', 'wb', 'bw', 'wt', 'tw',
        'a', 'ab', 'ba', 'at', 'ta',
        ]

    return value in accepted_modes


def output_stats(profile, sorting, stream: IO = stdout) -> None:
    p = Stats(profile, stream=stream)
    p.sort_stats(sorting)
    p.print_stats()
