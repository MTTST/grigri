# -*- coding: utf-8 -*-
"""
    grigri.dates.range
    ~~~~~~~~~~~~~~~~~~

    Methods for dynamically generating a range of dates e.g. a date range
    for the current month.
"""

from datetime import datetime

import pandas as pd

__all__ = [
    'day_range',
    'date_range',
    'month_range',
    'quarter_range'
]

def day_range(num_days, anchor_date=None, inclusive=True):
    """
    Returns a :class:`DatetimeIndex` object spanning the specified number of 
    days.

    :param num_days: Number of days to move forward (or backwards if negative) 
                     from the `anchor_date`. Corresponds to the length of the 
                     returned date range. 
    :param anchor_date: Datetime to begin counting from.
    :param inclusive: If `True` will include `anchor_date` as part of the
                      date_range

    >>> day_range(-6, datetime(2013,9,5), inclusive=False)
    <class 'pandas.tseries.index.DatetimeIndex'>
    [2013-08-30 00:00:00, ..., 2013-09-04 00:00:00]
    Length: 6, Freq: D, Timezone: None
    """

    assert num_days != 0, 'day_range must span at least one day'

    if anchor_date is None:
        anchor_date = datetime.now()

    shift = 1 if num_days > 0 else -1

    swing_date = anchor_date + timedelta(num_days - shift)

    if not inclusive:
        anchor_date += timedelta(shift)
        swing_date += timedelta(shift)

    if anchor_date > swing_date:
        anchor_date, swing_date = swing_date, anchor_date 

    return pd.date_range(anchor_date, swing_date, normalize=True)

def date_range(dt=None, freq='m', full_range=True):
    """
    Generic date range function. Also called by `month_range` and 
    `quarter_range`.
    """

    if dt is None:
        dt = datetime.now()

    start_date = _first_of(freq=freq, dt=dt)
    end_date = _end_of(freq=freq, dt=dt) if full_range else dt

    return pd.date_range(start_date, end_date, normalize=True)