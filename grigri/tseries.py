# -*- coding: utf-8 -*-
"""
    grigri.tseries
    ~~~~~~~~~~~~~~~~~~

    Transformations, reshapings and manipulations for 
    time-series DataFrames and Series.
"""

from datetime import datetime

import numpy as np
import pandas as pd

from .dates.scalar import strip_time


def group_resample(frame, date_column, groupby=None, level=None, 
                   value_column=None, freq='d', how='mean'):
    """
    Applies :func:`resample` to every group in a groupby object.

    :param frame: Target dataframe to transform.
    :param date_column: Column to set index when resampling. Column must 
                        contain only datetime values.
    :param groupby: Column or index to group `data_frame` by. This is 
                the same argument when using :func:`DataFrame.groupby()`
    :param level: Index level to groupby. Only supply groupby or level, not 
                  both.
    :param value_column: Column to use as the value for the time-series 
                         Series. If not specified, time-series will effectively
                         just count each timestamp.
    :param freq: Frequency to downsample or upsample time-series by.
    :param how: Name of or aggregation function to use when resampling.

    .. note ::
        This function *always* returns a Series -- possibly with a `MultiIndex`. 
        It will never return a DataFrame as if there are any columns after the 
        aggregation step, it will call :func:`stack` to reduce the result into a 
        Series.
    """
    
    # if no value column is supplied to aggregate, make sure resampling
    # just counts the number of timestamps
    if value_column is None:
        value_column = date_column
        how = 'count'

    grouped = frame.groupby(by=groupby, level=level, squeeze=True)

    def f(chunk):
        chunk = chunk.set_index(date_column, drop=False)[value_column]
        return chunk.resample(freq, how=how)

    result = grouped.apply(f)

    # Sometimes squeeze doesn't reduce the result from DataFrame
    # to Series. Stack manually.
    try:
        result = result.stack()
    except AttributeError:
        pass

    return result

def split_tseries(frame, split_date=None):
    """
    Splits a time-series DataFrame(or Series) into one DataFrame before the 
    split date and another DataFrame after the split date.
    
    :param data_frame: Target DataFrame or Series to split. Must have a 
                       :class:`DatetimeIndex` as its index.
    :param split_date: Date to split on, defaults to current day.

    >>> data.head()
    2013-09-01    1
    2013-09-02    1
    ...
    2013-09-29    1
    2013-09-30    1
    Freq: D, dtype: int64
    >>> past, future = split_tseries(data, datetime(2013,9,2))
    >>> past
    2013-09-01    1
    2013-09-02    1
    Freq: D, dtype: int64
    >>> future
    2013-09-03    1
    2013-09-04    1
    ...
    2013-09-29    1
    2013-09-30    1
    Freq: D, dtype: int64

    .. note:: 
        Keep in mind that rows on the same day as `split_date` will be in the 
        "past" DataFrame.
    """

    if split_date is None:
        split_date = datetime.now()
    
    split_date = strip_time(split_date)
    
    # datetimeindex has to be sorted before slicing
    split_frame = frame.sort_index()
    
    return split_frame[:split_date], split_frame[split_date:]

def count_timestamps(series, freq='d'):
    assert series.dtype == '<M8[ns]', "Series must have datetime64 datatype"

    tseries = pd.Series(1, index=series)

    return tseries.resample(freq, how='sum')

def resample_reindex(tseries, new_index, freq='d', how='mean',
                     fill_value=None):
    """
    Performs a pandas :func:`resample` and :func:`reindex` at the same time. 

    This function is syntactic sugar for a very common resampling techinque 
    where it's  necessary to force the index to conform to a specific date 
    range (e.g. a date range for a particular month) right after resampling.

    It is functionally equivalent to::

        tseries.resample(freq, how).reindex(new_index)
    """

    tseries = tseries.resample(freq, how=how).reindex(new_index)

    if fill_value is not None:
        tseries = tseries.fillna(fill_value)
    
    return tseries