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
from io import IOBase
from io import FileIO
from io import BytesIO
from io import StringIO
from sys import stdout
from sys import stderr
from pstats import Stats
from pstats import SortKey

from inspect import Parameter
from inspect import getfullargspec, signature
from typing import Any, Callable, IO, Literal, Union

from .errors import InvalidSortingMethod, InvalidMode


# Globals
MODE = Literal['a', 'ab', 'at', 'w', 'wb', 'wt']


def get_default_args(function: Callable, default: Any) -> dict:
    """Retrieves all Default Values of a Given Function.

    Args:
        function (Callable): A function to inspect
        default (Any): Define a Default Value when none exists

    Returns:
        (dict) A Dictionary of {arg name: arg default value} of a given function.

    """
    d = signature(function).parameters.items()
    return {key: val.default if val.default != Parameter.empty else default for key, val in d}


def default_arg(function: Callable, keyword: str, default: Any = None) -> Any:
    """Retrieves the Default Value of the Specified Keyword Argument if present.
    Args:
        function (Callable): A function to inspect
        keyword (str): keyword argument to find.
        default (Any): Define a Default Value when none exists
    Returns:
        (Any) The default value of a given keyword, from the specified function.

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

    Args:
        function (Callable): a callable function
        keyword (str): keyword argument name found in function
        args (tuple): Positional argument values delivered to function
        kwargs (dict): Keyword argument values delivered to function

    Returns:
        (bool | Any) the bool toggle of a specific keyword if present in function.

    Notes:
        - If keyword is not present as a valid argument of the function, returns False
        - Assumes the keyword value should be a boolean (toggle).

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
        value (str | pstats.SortKey): method used to sort profile results

    Returns:
        (bool) True if value is a valid sorting key, else False

    Raises:
        InvalidSortingMethod

    """
    isvalid = value in [
        *[i for i in SortKey],
        'calls', 'cumtime', 'cumulative', 'file', 'filename', 'line', 'module',
        'name', 'ncalls', 'nfl', 'pcalls', 'stdname', 'time', 'tottime',
    ]

    if not isvalid:
        raise InvalidSortingMethod(f"Invalid Sorting Method: {value}.")

    return isvalid


def is_valid_mode(value: MODE) -> bool:
    """Test if the value is a valid File Opening Mode.

    Args:
        value (MODE): mode used to open a file

    Returns:
        (bool) if mode is supported / valid

    Raises:
        InvalidMode

    """
    is_valid = value in ['a', 'ab', 'at', 'w', 'wb', 'wt']

    if is_valid is False:
        raise InvalidMode(f"Invalid Writing Method: ({value}).")

    return is_valid


def output_stats(profile, sorting, stream: IO = stdout) -> None:
    """Organize and delegate Profile results as prescribed.

    Args:
        profile (cProfile.Profile): profile class containing results
        sorting (str | pstats.SortKey): method used to sort results
        stream (IO): where to output results (stdout by default)

    Returns:
        (None) Profile results are sent to designated stream,
        which is stdout by default.

    """
    p = Stats(profile, stream=stream)
    p.sort_stats(sorting)
    p.print_stats()


class Statistics:
    __slots__ = ('stream', 'mode', 'sortby', 'output')

    def __init__(self,
                 stream: Union[str, StringIO, FileIO, BytesIO],
                 mode: MODE,
                 sortby: Any,
                 ):
        self.stream = stream or stdout
        self.mode = mode
        self.sortby = sortby

        if issubclass(self.stream.__class__, IOBase):
            self.output = self._write_it
        elif issubclass(self.stream.__class__, str):
            self.output = self._open_file
        else:
            raise ValueError(f"Invalid Stream or Filepath: {self.stream}")

    def _open_file(self, profile, name: str):
        with open(self.stream, self.mode) as f:
            f.write(f'Profiling {name}()\n')
            output_stats(profile, self.sortby, f)

    def _write_it(self, profile, name: str):
        self.stream.write(f'Profiling {name}()\n')
        output_stats(profile, self.sortby, self.stream)
