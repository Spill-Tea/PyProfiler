"""
    PyProfiler/Wrapper.py
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
from typing import Any, Callable
from cProfile import Profile as _Profile

from PyProfiler.utils import MODE
from PyProfiler.utils import Statistics
from PyProfiler.utils import check_keyword
from PyProfiler.utils import is_valid_mode
from PyProfiler.utils import is_valid_sortkey


class Profiler:
    """A Toggleable cProfile Wrapper to easily debug any Python Function.

    By default, 'debug' is the keyword argument used to toggle cProfile, but the keyword may be
    modified according to user specification. When, the keyword is set to True, the Function is
    then Profiled, providing output to the appropriate stream.

    Args:
        keyword (str): Keyword (or Positional) Argument to search for in the wrapped function.
        filepath (str): The path to save output of function profiling. If None, the profile stats
            are returned to stdout by default.
        mode (MODE): Mode used to write to filepath. Options: 'a' | 'ab' | 'at' | 'w' | 'wb' | 'wt'
        sortby (Any): Define how to sort Profiling Results for Visualization. For More Details:
            https://docs.python.org/3/library/profile.html#pstats.Stats.sort_stats
        kwargs (Any): Additional keyword arguments are supplied to cProfile.Profile class. See:
            https://docs.python.org/3/library/profile.html#profile.Profile

    Example Usage:

        '''python

            from PyProfiler import Profiler

            @Profiler(keyword='profile')
            def add(a, b, profile: bool = True):
                return a + b

            add(1, 2, profile=True)  # is profiled
            add(1, 2, True) # is profiled
            add(a=1, b=2, profile=True)  # is profiled
            add(1, 2, profile=True)  # is profiled
            add(1, 2, False)  # Not profiled
            add(1, 2, profile=False)  # Not profiled
            add(1, 2)  # is profiled

            @Profiler(keyword='verbose')
            def sub(a, b, verbose):
                return a - b

            sub(1, 2, True)  # is profiled
            sub(1, 2, verbose=True)  # is profiled

            sub(1, 2, False)  # Not profiled
            sub(1, 2, verbose=False)  # Not profiled
        '''

    Notes:
        - If the defined keyword is not a keyword or positional argument, the function will behave normally.
        - When using multiple wrappers, the Profiler wrapper must be the first wrapper.

    """
    def __init__(self,
                 keyword: str = 'debug',
                 filepath: Any = None,
                 mode: MODE = 'a',
                 sortby: Any = 'cumulative',
                 **kwargs
                 ) -> None:
        # Sanity Checks - Raise errors immediately (not after profiling)
        is_valid_mode(mode)
        is_valid_sortkey(sortby)

        self.keyword = keyword
        self._stream = Statistics(
            stream=filepath,
            mode=mode,
            sortby=sortby
        )
        self.kwargs = kwargs

    def __call__(self, function: Callable):
        def wrapper(*args, **kwargs):
            if not check_keyword(function, self.keyword, *args, **kwargs):
                return function(*args, **kwargs)

            prof = _Profile(**self.kwargs)
            ret_val = prof.runcall(function, *args, **kwargs)
            self._stream.output(prof, function.__qualname__)

            return ret_val

        return wrapper
