# -*- coding: utf-8 -*-
"""
    grigri.tools
    ~~~~~~~~~~~~~~~~~~

    Miscellaneous functions for dealing with type-checking.
"""

from datetime import datetime, date
from math import pi, sin, cos, atan2, sqrt, floor, ceil

import pandas as pd

from dateutil.parser import parse


def is_null(*args):
    """
    Returns the first non-null value. Similar to T-SQL COALESCE() function.

    >>> is_null(None, float('nan'), 'hello')
    'hello'
    """

    for k in args:
        if not pd.isnull(k):
            return k

    # if everything is null then return the last argument
    return args[-1]

def is_numeric(n):
    """
    Tests if an object is interpretable as a number.

    >>> is_numeric('1')
    True
    """

    try:
        float(n)
        return True
    except (ValueError, TypeError):
        return False

def is_date(dt, strict=True):
    """
    Tests if an object is interpretable as a datetime object.

    :param dt: object to test as a datetime
    :param strict: If set to `False` will also try to interpret strings as
                    dates.
    """

    if isinstance(dt, (datetime, date)):
        return True

    if not strict:
        try:
            if dt not in (' ', '-', ''):
                parse(dt)
                return True
        except (AttributeError, ValueError):
            pass

    return False

def is_empty(data):
    """
    Checks if an object, particularly :class:`Series` and :class:`DataFrame`,
    contains any values.

    .. note:: 
        ``DataFrame`` objects have an ``empty`` attribute, but ``Series`` don't.
        This function allows you to check both data structures using only one 
        function.
    """
    
    try:
        return not bool(data)
    except ValueError:
        pass

    try:
        return data.empty
    # Series objects do not have an empty method, so check 
    # if there are any values
    except AttributeError:
        if data.tolist():
            return False
        return True

def percent_change(before, after):
    """
    Return percent change increase or decrease between two numbers.

    >>> percent_change(100, 110)
    0.1
    """

    try:
        return (1. * after - before) / before
    except ZeroDivisionError:
        return float('nan')

def find_column_name(frame, column_name):
    """
    Searches for the desired column in a DataFrame and returns its name.

    This situation arises when you pull data from a data source (e.g. SQL) 
    and you know the column name is installationid, but case-sensitivity may be 
    an issue.
    """

    column_match = column_name.lower()

    for col in frame.columns:
        if col.lower() == column_match:
            return col

    raise KeyError("Cannot find column in DataFrame: %s" % column_name)

def split_sequence(data, n):
    """
    Splits a Series or DataFrame (or any list-like object) into chunks.

    :param data: List-like data-structure (list, DataFrame, Series,...) to 
                 be split. 
    :param n: Number of chunks to split `data` into. Chunks will be as equal
              size as possible.

    .. warning::
        Data is not sorted by ``split_sequence`` and will be split as given. 
        You must pre-sort if necessary.
    """
    L = len(data)

    split_size = int(ceil(1. * L / n))

    return (data[i:i+ split_size] for i in range(0, L, split_size))

def ditto(frames, meth, *args, **kwargs):
    """
    Applies the same method to one or more DataFrames. Any args or kwargs necessary 
    to call `meth` should also be passed in.

    :param frames: List of DataFrames.
    :param meth: Name of DataFrame method to call on each DataFrame in `frames`.
    """

    return [getattr(frame, meth)(*args, **kwargs) for frame in frames]
