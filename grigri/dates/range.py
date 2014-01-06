# -*- coding: utf-8 -*-
"""
    grigri.dates.range
    ~~~~~~~~~~~~~~~~~~

    Methods for dynamically generating a range of dates e.g. a date range
    for the current month.
"""

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from functools import partial

import pandas as pd

from .scalar import first_of, end_of

__all__ = [
    'date_range', 'week_range', 'month_range','quarter_range', 'year_range',
    'swing_range', 'day_swing', 'week_swing', 'month_swing', 'year_swing'
]

freq_map = {
    'd': 'days',
    'w': 'weeks',
    'm': 'months',
    'y': 'years'
}

def date_range(dt=None, freq='m', full_range=True):
    """
    Returns a date range for the specified frequency e.g. all the 
    dates in a particular month or quarter.

    :param dt: Datetime that determines the time period to use
    :param freq: Frequency of the time period e.g. 'w', 'm' or 'q'
    :param full_range: If `True` will return a date range for the 
                        entire period. Otherwise, it will return a 
                        date range from the first of the period up 
                        to `dt`.
    """

    if dt is None:
        dt = datetime.now()

    start_date = first_of(dt=dt, freq=freq)
    end_date = end_of(dt=dt, freq=freq) if full_range else dt

    return pd.date_range(start_date, end_date, normalize=True)

week_range = partial(date_range, freq='w')
month_range = partial(date_range, freq='m')
quarter_range = partial(date_range, freq='q')
year_range = partial(date_range, freq='y')

def swing_range(periods, anchor_date=None, freq='d', inclusive=True):
    """
    Returns a range of dates spanning the specified number of 
    days.

    :param periods: Number of days to move forward (or backwards if negative) 
                     from the `anchor_date`. Corresponds to the length of the 
                     returned date range. 
    :param anchor_date: Datetime to begin counting from.
    :param inclusive: If `True` will include `anchor_date` as part of the
                      date_range

    >>> swing_range(-6, datetime(2013,9,5), inclusive=False, freq='d')
    <class 'pandas.tseries.index.DatetimeIndex'>
    [2013-08-30 00:00:00, ..., 2013-09-04 00:00:00]
    Length: 6, Freq: D, Timezone: None
    """

    freq_name = freq_map[freq]
    
    if anchor_date is None:
        anchor_date = datetime.now()
    
    shift = 1 if periods > 0 else -1
    
    if not inclusive:
        anchor_date += relativedelta(**{freq_name: shift})
    
    swing_date = anchor_date + relativedelta(**{freq_name: periods})

    if anchor_date > swing_date:
        anchor_date, swing_date = swing_date, anchor_date

    # For weeks, months, yrs, you have to deal with
    # the end or the beginning of the interval depending on
    # if you are moving forwards or backwards in time.
    # You don't have to worry about days because the time component will be
    # stripped when you normalize in `date_range`
    if freq != 'd':
        swing_date = end_of(swing_date, freq=freq) if periods >= 0 else first_of(swing_date, freq=freq)

    return pd.date_range(anchor_date, swing_date, normalize=True, freq=freq)

day_swing = partial(swing_range, freq='d')
week_swing = partial(swing_range, freq='w')
month_swing = partial(swing_range, freq='m')
year_swing = partial(swing_range, freq='y')
