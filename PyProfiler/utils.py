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
from sys import stdout, stderr
from pstats import SortKey, Stats
from typing import Any, Callable, IO

from inspect import Parameter
from inspect import getfullargspec, signature

from .errors import InvalidSortingMethod, InvalidMode


def get_default_args(function: Callable, default: Any) -> dict:
    """Retrieves all Default Values of a Given Function.

    Args:
        function (Callable): A function to inspect
        default (Any): Define a Default Value when none exists

    Returns (dict):
        A Dictionary of {args: default value} of a given function.

    """
    d = signature(function).parameters.items()
    return {key: val.default if val.default != Parameter.empty else default for key, val in d}


def default_arg(function: Callable, keyword: str, default: Any = None) -> Any:
    """Retrieves the Default Value of the Specified Keyword Argument if present.
    Args:
        function (Callable): A function to inspect
        keyword (str): keyword argument to find.
        default (Any): Define a Default Value when none exists
    Returns (Any):
        The default value of a given keyword, from the specified function.

    NOTE: If the function does not have a given keyword argument, the default value is returned.

    """
    try:
        ret_val = signature(function).parameters[keyword]
        if ret_val.default == Parameter.empty:
            return default
        return ret_val.default
    except KeyError:
        return default


def check_keyword(function: Callable, keyword: str, *args, **kwargs):
    """Retrieves the value of a keyword of an intercepted function.
    NOTE: Assumes keyword value should be a boolean (toggle).

    Args:
        function (Callable): a callable function
        keyword (str): keyword argument name found in function
        args (tuple): Positional argument values delivered to function
        kwargs (dict): Keyword argument values delivered to function

    Returns (bool | Any):
        the bool toggle of a specific keyword if present in function.
        NOTE: If keyword is not present as a valid argument of the function, returns False

    """
    specs = getfullargspec(function)

    # Function must have the specified Keyword Argument
    if keyword not in specs.args:
        print(f"Warning: Keyword Not Available in Function: {keyword}", file=stderr)
        return False

    # If function comes from a class, eliminate the first arg name and value
    if specs.args[0] in ['self', 'cls']:
        positional_args = dict(zip(specs.args[1:], args[1:]))
    else:
        positional_args = dict(zip(specs.args, args))

    # Check Keyword Args --> Positional Args --> Default Values --> False
    key_value = kwargs.get(
        keyword,
        positional_args.get(
            keyword,
            default_arg(function, keyword, False)
        )
    )

    return key_value and isinstance(key_value, bool)


def is_valid_sortkey(value: Any) -> bool:
    """Tests if the value is a valid Sorting Method accepted by cProfile and pstats Stats libraries.

    Args:
        value: (str | pstats.SortKey)

    Returns: (bool) True if value is a valid sorting key, else False
    Raises: InvalidSortingMethod

    """
    isvalid = value in [
        'calls', 'cumtime', 'cumulative', 'file', 'filename', 'line', 'module',
        'name', 'ncalls', 'nfl', 'pcalls', 'stdname', 'time', 'tottime'
    ]

    try:
        return isvalid or value in SortKey
    except TypeError:
        raise InvalidSortingMethod(f"Invalid Sorting Method: {value}.")


def is_valid_mode(value: str) -> bool:
    """Test if the value is a valid File Opening Mode.

    Args:
        value (str): mode used to open a file

    Returns: (bool) if mode is supported / valid
    Raises: InvalidMode

    """
    accepted_modes = [
        'w', 'w+', 'wb', 'bw', 'w+b', 'bw+', 'wt', 'tw', 'w+t', 'tw+',
        'a', 'a+', 'ab', 'ba', 'a+b', 'ba+', 'at', 'ta', 'a+t', 'ta+',
        ]

    is_valid = value in accepted_modes
    if is_valid is False:
        raise InvalidMode(f"Invalid Writing Method: ({value}).")

    return is_valid


def output_stats(profile, sorting, stream: IO = stdout) -> None:
    """Organize and delegate Profile results as prescribed.

    Args:
        profile (cProfile.Profile): profile class containing results
        sorting (str | pstats.SortKey): method used to sort results
        stream (IO): where to output results

    Returns: (None)

    """
    p = Stats(profile, stream=stream)
    p.sort_stats(sorting)
    p.print_stats()
