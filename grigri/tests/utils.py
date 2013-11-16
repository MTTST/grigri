"""

Utility methods used in testing. For example `assert_frame_equal`
checks if two DataFrames are equal by looking at indexes, dtypes,
values, etc.

Functions directly taken from pandas source code:
https://github.com/pydata/pandas/blob/master/pandas/util/testing.py

"""

import numpy as np

from pandas.core.common import isnull
from pandas import DataFrame


def isiterable(obj):
    return hasattr(obj, '__iter__')

def assert_almost_equal(a, b, check_less_precise = False):
    if isinstance(a, dict) or isinstance(b, dict):
        return assert_dict_equal(a, b)

    if isinstance(a, str):
        assert a == b, "%s != %s" % (a, b)
        return True

    if isiterable(a):
        np.testing.assert_(isiterable(b))
        na, nb = len(a), len(b)
        assert na == nb, "%s != %s" % (na, nb)

        if np.array_equal(a, b):
            return True
        else:
            for i in range(na):
                assert_almost_equal(a[i], b[i], check_less_precise)
        return True

    err_msg = lambda a, b: 'expected %.5f but got %.5f' % (b, a)

    if isnull(a):
        np.testing.assert_(isnull(b))
        return

    if isinstance(a, (bool, float, int, np.float32)):
        decimal = 5

        # deal with differing dtypes
        if check_less_precise:
            dtype_a = np.dtype(type(a))
            dtype_b = np.dtype(type(b))
            if dtype_a.kind == 'f' and dtype_b == 'f':
                if dtype_a.itemsize <= 4 and dtype_b.itemsize <= 4:
                    decimal = 3

        if np.isinf(a):
            assert np.isinf(b), err_msg(a, b)

        # case for zero
        elif abs(a) < 1e-5:
            np.testing.assert_almost_equal(
                a, b, decimal=decimal, err_msg=err_msg(a, b), verbose=False)
        else:
            np.testing.assert_almost_equal(
                1, a / b, decimal=decimal, err_msg=err_msg(a, b), verbose=False)
    else:
        assert a == b, "%s != %s" % (a, b)

def assert_dict_equal(a, b, compare_keys=True):
    a_keys = frozenset(a.keys())
    b_keys = frozenset(b.keys())

    if compare_keys:
        assert(a_keys == b_keys)

    for k in a_keys:
        assert_almost_equal(a[k], b[k])

def assert_series_equal(left, right, check_dtype=True,
                        check_index_type=False,
                        check_index_freq=False,
                        check_series_type=False,
                        check_less_precise=False):
    if check_series_type:
        assert(type(left) == type(right))
    assert_almost_equal(left.values, right.values, check_less_precise)
    if check_dtype:
        assert(left.dtype == right.dtype)
    if check_less_precise:
        assert_almost_equal(left.index.values, right.index.values, check_less_precise)
    else:
        assert(left.index.equals(right.index))
    if check_index_type:
        assert(type(left.index) == type(right.index))
        assert(left.index.dtype == right.index.dtype)
        assert(left.index.inferred_type == right.index.inferred_type)
    if check_index_freq:
        assert(getattr(left, 'freqstr', None) ==
               getattr(right, 'freqstr', None))


def assert_frame_equal(left, right, check_dtype=True,
                       check_index_type=False,
                       check_column_type=False,
                       check_frame_type=False,
                       check_less_precise=False,
                       check_names=True):
    if check_frame_type:
        assert(type(left) == type(right))
    assert(isinstance(left, DataFrame))
    assert(isinstance(right, DataFrame))

    if check_less_precise:
        assert_almost_equal(left.columns,right.columns)
        assert_almost_equal(left.index,right.index)
    else:
        assert(left.columns.equals(right.columns))
        assert(left.index.equals(right.index))

    for i, col in enumerate(left.columns):
        assert(col in right)
        lcol = left.icol(i)
        rcol = right.icol(i)
        assert_series_equal(lcol, rcol,
                            check_dtype=check_dtype,
                            check_index_type=check_index_type,
                            check_less_precise=check_less_precise)

    if check_index_type:
        assert(type(left.index) == type(right.index))
        assert(left.index.dtype == right.index.dtype)
        assert(left.index.inferred_type == right.index.inferred_type)
    if check_column_type:
        assert(type(left.columns) == type(right.columns))
        assert(left.columns.dtype == right.columns.dtype)
        assert(left.columns.inferred_type == right.columns.inferred_type)
    if check_names:
        assert(left.index.names == right.index.names)
        assert(left.columns.names == right.columns.names)