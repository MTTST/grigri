# -*- coding: utf-8 -*-
"""
    grigri.constructors
    ~~~~~~~~~~~~~~~~~~

    Functions that produce DataFrames and Series with only 
    scalar arguments.
"""

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
                "with length greater than zero: {}".format(date_index))

    straight_line = pd.Series(value_per_unit_time, index=date_range)

    if cumsum:
        return straight_line.cumsum()

    return straight_line

