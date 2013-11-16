# -*- coding: utf-8 -*-
"""
    grigri.dates.scalar
    ~~~~~~~~~~~~~~~~~~

    Scalar functions that perform an operation on a date and return 
    a string, numeric or date value.
"""

from datetime import datetime

from functools import partial

import pandas as pd
from pandas.tseries.offsets import (Week, MonthEnd, QuarterEnd, YearEnd, 
                                    DateOffset, MonthBegin, QuarterBegin,
                                    YearBegin)


__all__ = [
    'strip_time',
    'first_of', 'first_of_week', 'first_of_month', 'first_of_quarter',
    'first_of_year',
    'end_of', 'end_of_week', 'end_of_month', 'end_of_quarter', 
    'end_of_year',
    'prorate'
]

def strip_time(dt):
    """
    Returns datetime object stripped of time information.

    >>> strip_time(datetime(2013, 9, 5, 17, 1, 52, 661000))
    datetime.datetime(2013, 9, 5, 0, 0)
    """

    return datetime(dt.year, dt.month, dt.day)

_offset_begin_map = {
    'w': Week(weekday=0),
    'm': MonthBegin(),
    'q': QuarterBegin(startingMonth=1),  # FOQ = 1/1, 4/1, 7/1, 10/1
    'y': YearBegin(),
}

def first_of(dt=None, freq='m'):
    """
    Returns the first day of a given time period e.g. first of the month, 
    first of the quarter, etc.

    :param freq: Frequency of desired period, must be one of 'w', 'm', 'q' 
                 or 'y'.
    :param dt: Datetime that determines the particular time period to use.

    >>> first_of('m', datetime(2013, 5, 15))
    datetime(2013, 5, 1)
    """

    if dt is None:
        dt = datetime.now()

    try:
        offset = _offset_begin_map[freq.lower()]
    except KeyError:
        raise ValueError("Frequency not recognized: {}".format(freq)) 

    offset_date = offset.rollback(dt)

    return strip_time(offset_date)

# generate more semantic function names for `first_of`
# and `end_of`
first_of_week = partial(first_of, freq='w')
first_of_month = partial(first_of, freq='m')
first_of_quarter = partial(first_of, freq='q')
first_of_year = partial(first_of, freq='y')

_offset_end_map = {
    'w': Week(weekday=0),  # weekday: specific day of week. 0 for Monday
    'm': MonthEnd(),
    'q': QuarterEnd(startingMonth=12),  #startingMonth: EOQ = 12/31, 3/31, 6/30, 9/30
    'y': YearEnd(),
}


def end_of(dt=None, freq='m'):
    """
    Returns the last day of a given time period e.g. end of the month, end of 
    the quarter, etc.

    :param freq: Frequency of desired period, must be one of 'w', 'm', 'q' 
                 or 'y'.
    :param dt: Datetime that determines the particular time period to use.

    >>> end_of('m', datetime(2013, 5, 15))
    datetime(2013, 5, 31)
    """

    if dt is None:
        dt = datetime.now()

    try:
        offset = _offset_end_map[freq.lower()]
    except KeyError:
        raise ValueError("Frequency not recognized: {}".format(freq)) 

    offset_date = offset.rollforward(dt)

    return strip_time(offset_date)

end_of_week = partial(end_of, freq='w')
end_of_month = partial(end_of, freq='m')
end_of_quarter = partial(end_of, freq='q')
end_of_year = partial(end_of, freq='y')


def prorate(dt=None, freq='m'):
    """
    Pro-rates the current day over its current month, quarter 
    or year and returns a percentage.

    :param dt: Day to compute pro-rated amount with
    :param freq: Time frequency to consider. Use 'm' for 
                 month proration, 'q' for quarter, etc.

    >>> prorate(datetime(2013,9,26), freq='m')
    0.8666666666666667
    >>> prorate(datetime(2013,9,26), freq='y')
    0.736986301369863
    """

    if dt is None:
        dt = datetime.now()

    days = pd.date_range(first_of(dt, freq), end_of(dt, freq))

    numerator = dt - days.min()

    return (numerator.days + 1) / len(days)

