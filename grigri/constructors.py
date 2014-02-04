# -*- coding: utf-8 -*-
"""
    grigri.constructors
    ~~~~~~~~~~~~~~~~~~

    Functions that produce DataFrames, Series, etc. with lower dimensional
    arguments.
"""

import itertools

import pandas as pd


def straight_line(value, date_range, cumsum=True):
    """
    Amortizes a value across a date range using a straight-line method.

    :param value: Numeric amount to spread evenly across a time period.
    :param date_range: Desired time period to return time-series as.
    :param cumsum: If `True` return straight line Series as a cumulative sum
    """

    denominator = float(len(date_range))

    try:
        value_per_unit_time = value / denominator
    except ZeroDivisionError as e:
        raise e("Straight-line interpolation requires a date range "
                "with length greater than zero: {}".format(date_range))

    straight_line = pd.Series(value_per_unit_time, index=date_range)

    if cumsum:
        return straight_line.cumsum()

    return straight_line

def cartesion_index(*args, names=None):
    """
    Generates a `MultiIndex` from the cartesian product of multiple lists. 

    >>> make_index(['Los Angeles', 'San Diego', 'Bakersfield'], 
                   ['Residential', 'Commercial'])
    MultiIndex
    [(u'Los Angeles', u'Residential'), (u'Los Angeles', u'Commercial'), 
     (u'San Diego', u'Residential'), (u'San Diego', u'Commercial'), 
     (u'Bakersfield', u'Residential'), (u'Bakersfield', u'Commercial')]

    """
    cartesian_product = list(itertools.product(*args))

    return pd.MultiIndex.from_tuples(cartesian_product, names=names)

def empty_date_range():
    """Returns a :class:`DatetimeIndex` object with length zero."""

    # not sure how to initialize an empty date range
    # but a hacky way to do it is to set the end date
    # before the start date:
    return pd.date_range('08-01-2013', '07-31-2013')

def empty_series(name=None, as_time_series=False):
    """
    Returns an empty Series object.

    :param name: Name of Series object
    :param as_time_series: If true, will make index a 
                            DateTimeIndex so that the Series
                            is a time-series.
    """

    index = empty_date_range() if as_time_series else []

    return pd.Series(name=name, index=index)

def empty_frame(columns=None, as_time_series=False):
    """
    Returns an empty DataFrame object.

    :param columns: List of column names to use on DataFrame
    :param as_time_series: If true, will make index a DatetimeIndex so that 
                            the DataFrame is still a "time-series" and can 
                            still be resampled, etc.
    """

    if columns is None:
        columns = []

    index = empty_date_range() if as_time_series else []

    return pd.DataFrame(index=index, columns=columns)


