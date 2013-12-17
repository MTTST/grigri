# -*- coding: utf-8 -*-
"""
    grigri.tools
    ~~~~~~~~~~~~~~~~~~

    Miscellaneous functions for dealing with type-checking.
"""

from datetime import datetime, date

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