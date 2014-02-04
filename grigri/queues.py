"""
grigri.queues
~~~~~~~~~~~~~

This module is a library for computing the fundamental operations metrics: 
backlog, throughput rates, arrival rates, and wait times. These formulas can be
used on any "queue-like" system.
"""

from datetime import datetime
from dateutil.parser import parse

import numpy as np
import pandas as pd

from .tools import is_null


def flow_extract(df, flow_date_column, weight_column=None, freq='d'):
    """
    Returns a time-series of all timestamps of a flow column.

    This function is a convenience tool for quickly extracting 
    the necessary "inflows" and "outflows" Series needed for the actual
    formulas in this module.

    :param df: Target DataFrame containing raw data.
    :param flow_date_column: Column in `df` that contains the timestamps of 
                             units moving in or out of the queue.
    :param weight_column: Column in `df` that can be used to weight each unit 
                          that flows through the queue e.g. system size of a job.
                          If not set, will just count the number of units in 
                          each time period.
    :param freq: Frequency to downsample or upsample by. This should almost 
                 always be left as 'd'.
    """

    start_date = is_null(df[flow_date_column].min(), datetime.now())
    end_date = is_null(df[flow_date_column].max(), datetime.now())
    original_date_range = pd.date_range(start_date, end_date, normalize=True,
                                        freq=freq) 

    if weight_column:
        flow = df[[flow_date_column, weight_column]].dropna()
        flow = flow.set_index(flow_date_column)[weight_column]

        flow = flow.resample(freq, how='sum')
    # if no weight column specified, count the number of dates instead
    # of summing the weight column
    else:
        flow = df.set_index(flow_date_column, drop=False)[flow_date_column]
        flow = flow.dropna()

        flow =flow.resample(freq, how='count')

    flow = flow.reindex(original_date_range).fillna(0)

    return flow

# TODO: fix this function up and properly document it
def double_flow_extract(df, inflow_column, outflow_column, flow_date_column, 
                        freq='d'):
    """
    Returns two Series one for outflows and one for inflows from one DataFrame.
    Also see :func:`flow_extract`.

    :param df: Target DataFrame containing raw data.
    :param inflow_column: Column containing timestamps of units flowing into
                          the queue
    :param outflow_column: Column containing the timestamps of units flowing 
                            out of the queue
    :param flow_date_column: 
    """

    raw_inflows = df[[inflow_column, flow_date_column]].dropna()
    inflows = flow_extract(raw_inflows, flow_date_column, freq=freq)

    raw_outflows = df[[outflow_column, flow_date_column]].dropna()
    outflows = flow_extract(raw_outflows, flow_date_column, freq=freq)

    return inflows, outflows

def queues(inflow, outflow, current_backlog, time_index=None, inflow_column="Created", 
            outflow_column="Closed", weight_column=None, freq='d'):
    """
    Returns series for each of the main queueing metrics: arrivals, throughput 
    and backlog.

    :param inflow: DataFrame containing inflow data
    :param outflow: DataFrame containing outflow data
    :param current_backlog: Current total backlog.
    :param time_index: Date range to reindex the results by.
    :param inflow_column: Inflow timestamp column.
    :param outflow_column: Outflow timestamp column.
    :param weight_column: Column to wait units by.
    """

    inflow = flow_extract(inflow, inflow_column, weight_column, freq=freq)
    outflow = flow_extract(outflow, outflow_column, weight_column, freq=freq)

    if time_index is None:
        start_date = min(inflow.index.min(), outflow.index.min())
        end_date = max(inflow.index.max(), outflow.index.max())

        time_index = pd.date_range(start_date, end_date, normalize=True, freq=freq)

    inflow = inflow.reindex(time_index, fill_value=0)
    outflow = outflow.reindex(time_index, fill_value=0)

    backlog = reverse_backlog(inflow, outflow, backlog_start=current_backlog, freq=freq)

    return inflow, outflow, backlog

def _cumsum(flow):
    """
    Returns the cumulative sum of a time series, but will also reindex the 
    time-series to always range from its minimum date to today.
    """

    start_date = flow.index.min()
    end_date = datetime.now()
    full_range = pd.date_range(start_date, end_date, normalize=True)

    reindexed_flow = flow.reindex(full_range, fill_value=0)

    return reindexed_flow.cumsum()

def reverse_backlog(inflows, outflows, backlog_start, date_start=None, 
                    freq='d'):
    """
    Reconstructs historical backlog of a queue as a timeseries. Takes a 
    specified date with a given backlog number and backtracks historical
    backlog from inflow and outflow history.

    Args:
        inflows: Series
            A time-series containing a timestamp for each job that enters the 
            queue. 
        outflows: Series
            A time-series containing a timestamp for each job that leaves the 
            queue.
        backlog_start: int, float
            Known value of backlog at the date of `date_start`
        date_start: datetime or str, optional
            Date of the known value of `backlog_start`; this is the date that
            inflows and outflows will be added to. Defaults to today
        freq: str ['d', 'w', 'm', 'a']
            pandas date offset string which specifies the frequency of the
            returned time-series.
    """

    if date_start is None:
        date_start = datetime.now()

    if isinstance(date_start, str):
        date_start = parse(date_start)

    inflows = inflows[:date_start]
    outflows = outflows[:date_start]
    
    # flip order of time series to do reverse cumsum

    cum_inflow = inflows.sort_index(ascending=False).fillna(0).cumsum()
    cum_outflow = outflows.sort_index(ascending=False).fillna(0).cumsum()

    backlog = backlog_start - cum_inflow + cum_outflow
    backlog = backlog.fillna(method='ffill')

    # flip result back so timeseries is ascending
    backlog = backlog.sort_index()

    backlog = backlog.resample(freq, how='first')

    # backlog must be a non-negative number
    backlog[backlog < 0 ] = 0
    return backlog


def backlog(inflows, outflows, freq='d'):
    """
    Returns a time-series of historical backlog of a queue.

    Args:
        inflows: Series
            A time-series containing a timestamp for each job that enters the 
            queue. 
        outflows: Series
            A time-series containing a timestamp for each job that leaves the 
            queue.
        freq: str ['d', 'w', 'm', 'a']
            pandas date offset string which specifies the frequency of the
            returned time-series.
    """

    inflows = _cumsum(inflows)
    outflows = _cumsum(outflows)

    L = inflows.sub(outflows, fill_value=0)

    # on irregular resampling it's possible to get dates outside
    # the original time series. This step guarantees the returned
    # time-series is within the original date range
    begin_date, end_date = L.index.min(), L.index.max()
    return L.resample(freq, how='first')[begin_date: end_date]

def throughput(outflows, freq='d'):
    """
    Returns a time series of total throughput over a given interval.
    
    Args:
        outflows: Series
            A  time series containing a timestamp for each job that leaves the 
            queue.
        freq: str ['d', 'w', 'm', 'a']
            pandas date offset string which specifies the frequency of the
            returned time-series.
    """

    outflows = _cumsum(outflows)
    result = outflows.sub(outflows.shift(1), fill_value=0)

    return result.resample(freq, how='sum').fillna(0)

def arrivals(inflows, freq='d'):
    """
    Returns a time series of total arrivals over a given interval.
    
    Args:
        outflows: Series
            A  time series containing a timestamp for each job that enters the 
            queue.
        freq: str ['d', 'w', 'm', 'a']
            pandas date offset string which specifies the frequency of the
            returned time-series.
    """

    inflows = _cumsum(inflows)
    result = inflows.sub(inflows.shift(1), fill_value=0)

    return result.resample(freq, how='sum').fillna(0)

def wait(inflows, outflows, freq='m'):
    """Returns a Series of average wait times computed using Little's Law."""

    L = backlog(inflows, outflows, freq)
    k = arrivals(inflows, freq)

    w = L.resample(freq, how='mean') / k.resample(freq, how='mean')

    return w.dropna()