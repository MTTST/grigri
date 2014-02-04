# -*- coding: utf-8 -*-
"""
    grigri.transforms
    ~~~~~~~~~~~~~~~~~~

    Functions that transform Series and DataFrames.
"""

import pandas as pd

def squeeze(frame):
    """
    Attempts to reduce a DataFrame into a Series. Will raise ValueError if 
    unable to perform. Can also be used to infer time-series.
    """

    # Trivial case: squeeze cannot make a Series
    # any smaller
    if isinstance(frame, pd.Series) or len(frame.columns) == 0:
        return frame

    num_columns = len(frame.columns)

    # single column DataFrame -> select out only column to return a series
    if num_columns == 1:
        return frame.ix[:,0]

    if num_columns == 2:
        # detect any datetime columns
        for col in frame.columns:
            if frame[col].dtype == 'datetime64[ns]':
                datetime_column = col
                break
        else:
            raise ValueError

        return frame.set_index(datetime_column).ix[:0]

    raise ValueError

def remove_columns(frame, columns):
    """
    Returns a new DataFrame removing specified columns.

    :param frame: Target DataFrame to remove columns from.
    :param columns: Column or list of columns to remove from DataFrame. Is 
                    case-insensitive.
    """

    if not isinstance(columns, list):
        columns = [columns,]

    # case insensitive list of columns
    cols_to_remove = [c.lower() for c in columns]

    remaining_cols = [col for col in data_frame.columns 
                      if col.lower() not in cols_to_remove]

    return data_frame[remaining_cols]
