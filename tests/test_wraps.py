"""
    PyProfiler
        tests/test_wraps.py

"""
# import sys
import pytest
#
# from io import StringIO

from .functions import Math

add = (Math, 'add', 'verbose')
product = (Math, 'product', 'debug')


@pytest.mark.parametrize('cls, name, kwd, k_val, value, expect', [
    (*add, True, [1, 2, 3], 6),
    (*add, False, [1, 2, 3], 6),
    (*product, True, [1, 2, 3], 6),
    (*product, False, [1, 2, 3], 6),
])
def test_wrapped_methods(cls, name, kwd, k_val, value, expect):
    m = cls(value)
    f = getattr(m, name)
    assert f(**{kwd: k_val}) == expect


@pytest.mark.parametrize('cls, name, kwds, value, attrib', [
    (Math, 'new', {'debug': True}, [1, 3, 5], '_n'),
    (Math, 'new', {'debug': False}, [1, 3, 5], '_n')
])
def test_wrapped_classmethod(cls, name, kwds, value, attrib):
    """Test that wrapped Classmethods can still access the class it is derived from."""
    m = cls(value)
    previous = getattr(cls, attrib)
    f = getattr(m, name)
    ret = f(value, **kwds)
    assert isinstance(ret, cls)
    assert previous != getattr(cls, attrib)
