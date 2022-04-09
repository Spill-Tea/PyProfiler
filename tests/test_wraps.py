"""
    PyProfiler
        tests/test_wraps.py

"""
# import sys
import pytest

from io import SEEK_END

from .functions import Math
from .functions import STREAM
from .functions import addition


add = (Math, 'add', 'verbose')
product = (Math, 'product', 'debug')


@pytest.mark.parametrize('cls, name, kwd, k_val, value, expect', [
    (*add, True, [1, 2, 3], 6),
    (*add, False, [1, 2, 3], 6),
    (*add, False, [0, 1, 2, 3], 6),
    (*product, True, [1, 2, 3], 6),
    (*product, False, [1, 2, 3], 6),
    (*product, False, [0, 1, 2, 3], 0),
    (None, addition, 'verbose', True, [1, 2, 3], 6),
    (None, addition, 'verbose', False, [1, 2, 3], 6),
    (None, addition, 'verbose', True, range(11), 55),
    (None, addition, 'verbose', False, range(11), 55)
])
def test_wrapped_methods(cls, name, kwd, k_val, value, expect):
    if cls is None:
        # testing functions (not methods within a class)
        assert name(value, **{kwd: k_val}) == expect
    else:
        m = cls(value)
        function = getattr(m, name)
        assert function(**{kwd: k_val}) == expect


@pytest.mark.parametrize('cls, name, kwds, value, attrib', [
    (Math, 'new', {'debug': True}, [1, 3, 5], '_n'),
    (Math, 'new', {'debug': False}, [1, 3, 5], '_n')
])
def test_wrapped_classmethod(cls, name, kwds, value, attrib):
    """Test that wrapped Classmethods can still access the class it is derived from."""
    previous = getattr(cls, attrib)
    m = cls(value)
    function = getattr(m, name)
    ret = function(value, **kwds)
    assert isinstance(ret, cls)
    assert previous != getattr(cls, attrib)


@pytest.mark.parametrize('cls, name, kwd, k_val, value, expect', [
    (*add, True, [1, 2, 3], 6),
    (*add, False, [1, 2, 3], 6),
    (*add, True, range(11), 55),
    (*add, False, range(11), 55),
    (*product, True, [1, 2, 3], 6),
    (*product, False, [1, 2, 3], 6),
    (*product, True, [4, 5, 6], 120),
    (*product, False, [4, 5, 6], 120),
])
def test_stream(cls, name, kwd, k_val, value, expect):
    # Catalog the length of the previous stream
    start = STREAM.seek(0, SEEK_END)

    # Call the (Profiled) Function
    m = cls(value)
    function = getattr(m, name)
    assert function(**{kwd: k_val}) == expect

    # Now read stream
    STREAM.seek(start)  # reset cursor to initial
    output = STREAM.read()

    if k_val:
        line_1 = f'Profiling {cls.__name__}.{name}()\n'
        assert line_1 in output
        assert 'Ordered by: cumulative time' in output
        assert 'ncalls  tottime  percall  cumtime  percall filename:lineno(function)' in output
    else:
        # Nothing is output to the stream if function is not profiled
        assert output == ''
