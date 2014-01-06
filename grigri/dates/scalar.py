# -*- coding: utf-8 -*-
"""
    grigri.dates.scalar
    ~~~~~~~~~~~~~~~~~~

    Scalar functions that perform an operation on a date and return 
    a string, numeric or date value.
"""

from datetime import datetime, timedelta
from functools import partial

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

import pandas as pd
from pandas.tseries.offsets import (Week, MonthEnd, QuarterEnd, YearEnd, 
                                    DateOffset, MonthBegin, QuarterBegin,
                                    YearBegin)

from . import FREQUENCY_MAP


__all__ = [
    'strip_time',
    'first_of', 'first_of_week', 'first_of_month', 'first_of_quarter',
    'first_of_year',
    'end_of', 'end_of_week', 'end_of_month', 'end_of_quarter', 
    'end_of_year',
    'prorate', 'is_current',
    'date_diff', 'date_add'
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

def date_diff(dt1, dt2, freq='d'):
    """ 
    Returns the difference of two dates based on the given frequency.

    :param dt1: datetime or string representing a datetime.
    :param dt2: datetime or string representing a datetime.
    :param freq: Time frequency to calculate the datetime frequency between
                 `dt1` and `dt2`

    .. note::
        For week difference calculations, a week is defined as the range
        from Monday to Sunday.

    >>> date_diff('7-22-2013', '8-4-2013')
    -13
    >>> date_diff('7-22-2013', '8-4-2013', freq='w')
    -1
    """

    if isinstance(dt1, str):
        dt1 = parse(dt1)
    if isinstance(dt2, str):
        dt2 = parse(dt2)

    # timedelta in datetime module doesn't have a nice datediff for months
    # so I use dateutil.relativedelta library here:
    diff = relativedelta(dt1, dt2)

    if freq == 'd':
        return diff.days

    elif freq == 'm':
        assert dt1.year > 0 and dt2.year > 0
        month1 = dt1.month + dt1.year * 12
        month2 = dt2.month + dt2.year * 12
        return month1 - month2
    # dateutil.relativedelta doesn't do weeks
    # so I use timedelta module in datetime here:
    elif freq == 'w':
        # normalize both dates by converting them to the monday in their 
        # respective week
        monday1 = (dt1 - timedelta(days=dt1.weekday()))
        monday2 = (dt2 - timedelta(days=dt2.weekday()))

        return (monday1 - monday2).days / 7

    elif freq in ('a', 'y'):
        return diff.years

    raise ValueError('Unknown freq format "{}". Can only take "d", "m", "w" or "y"'
        .format(freq))

def date_add(periods, freq='d', anchor_date=None):
    """
    Add a specified number of days, weeks, or months to a date.

    :param periods: Number of periods (e.g. days, weeks, months) to add to 
                    `anchor_date`. Can also be negative.
    :param freq: Frequency of the period ('d', 'w', 'm',...)
    :param anchor_date: Date to add periods to.
    """

    if anchor_date is None:
        anchor_date = datetime.now()

    frequency_name = FREQUENCY_MAP[freq]

    return anchor_date + relativedelta(**{frequency_name: periods})

def is_current(dt, freq='m'):
    """
    Checks if a date is in the current month, quarter or year.

    >>> datetime.now()
    datetime.datetime(2013, 9, 26, 16, 3, 7, 130000)
    >>> is_current(datetime(2013,9,26))
    True
    """

    # ideally would use `date_range` function in .range module, but that would 
    # lead to a circular import...
    dt_range = pd.date_range(first_of(dt, freq), end_of(dt,freq),
                             normalize=True, freq='d')

    return dt in dt_range
