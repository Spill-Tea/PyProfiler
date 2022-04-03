"""
    PyProfiler
        tests/functions.py

"""
from PyProfiler import Profiler


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


class ExampleProfiled:
    def __init__(self):
        pass

    @Profiler(keyword='verbose')
    def add(self, *args, verbose=True):
        return sum(args)

    @Profiler(keyword='debug')
    def subtract(self, *args, debug=False):
        pass
