"""
    PyProfiler
        tests/functions.py

"""
from math import prod
from io import StringIO

from PyProfiler import Profiler

# Globals
STREAM = StringIO()


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


class Math:
    _n = 1

    def __init__(self, values: list):
        self.values = values

    @Profiler(keyword='verbose', filepath=STREAM)
    def add(self, verbose: bool = True):
        return sum(self.values)

    @Profiler(filepath=STREAM)
    def product(self, debug: bool):
        return prod(self.values)

    @classmethod
    @Profiler(filepath=STREAM)
    def new(cls, values: list, debug: bool):
        cls._n += 1
        return cls(values)


@Profiler(keyword='verbose', filepath=STREAM)
def addition(values, verbose: bool = True):
    return sum(values)
